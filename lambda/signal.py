import json
import boto3
import pandas as pd
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))
now = datetime.now(KST)

s3 = boto3.client('s3')
# sagemaker = boto3.client('sagemaker')

BUCKET_NAME = "YOUR_BUCKET_NAME"
PREFIX = f'topics/btc_1m_kline_structured/{now.strftime("%Y-%m-%d")}/'
print(PREFIX)
#TODO
# training docker image uri
# sagemaker role
# DOCKER_IMAGE_URI=
# SAGEMAKER_ROLE_ARN=

def lambda_handler(event, context):
    now = datetime.now(KST)
    past = now - timedelta(hours=4)

    # Generate strings for today's and yesterday's dates (yyyy-mm-dd)
    today_str = now.strftime("%Y-%m-%d")
    yesterday = now - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")

    # Prepare a list of two prefixes for S3 paths
    prefixes = [
        f'topics/btc_1m_kline_structured/{yesterday_str}/',
        f'topics/btc_1m_kline_structured/{today_str}/'
    ]

    # Collect object keys whose LastModified is between 'past' and 'now'
    all_keys = []
    for prefix in prefixes:
        resp = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
        for obj in resp.get("Contents", []):
            # Convert LastModified to KST before comparison
            if past <= obj["LastModified"].astimezone(KST) <= now:
                all_keys.append(obj["Key"])

    # If no files to process, return early
    if not all_keys:
        return {
            'statusCode': 200,
            'body': json.dumps('No recent files to process')
        }

    # Read and parse each file into a DataFrame
    dfs = []
    for key in sorted(all_keys):
        try:
            s3_obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
            raw_content = s3_obj['Body'].read().decode('utf-8')
            raw_lines = raw_content.splitlines()

            parsed_rows = []
            for line in raw_lines:
                try:
                    # First unpack: JSON string is wrapped in quotes, e.g. "\"{...}\""
                    first_parse = json.loads(line)

                    # If the first parse returns a string, unpack again to get a dict
                    if isinstance(first_parse, str):
                        second_parse = json.loads(first_parse)
                    else:
                        second_parse = first_parse

                    parsed_rows.append(second_parse)
                except Exception as e:
                    print(f"Skipped line due to parse error: {e}")
                    continue

            # Convert parsed JSON objects into a DataFrame
            df_file = pd.DataFrame(parsed_rows)

            # Ensure 'timestamp' column exists before appending
            if 'timestamp' not in df_file.columns:
                print(f"⚠️ Skipping {key}: no 'timestamp' column")
                continue

            dfs.append(df_file)
            print(f"✅ Loaded {key} → Rows: {len(df_file)} Columns: {df_file.columns.tolist()}")
        except Exception as e:
            print(f"❌ Failed to process {key}: {e}")
            continue

    # If no valid DataFrames were created, return early
    if not dfs:
        print("⚠️ No valid dataframes to process. Exiting.")
        return {
            'statusCode': 200,
            'body': json.dumps('No valid data with timestamp column')
        }

    # Concatenate all DataFrames and sort by 'timestamp'
    df = pd.concat(dfs, ignore_index=True).sort_values(by='timestamp')
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Calculate 30-period and 120-period moving averages
    df['ma30'] = df['close'].rolling(window=30).mean()
    df['ma120'] = df['close'].rolling(window=120).mean()

    # Detect golden cross: 30-period MA crossing above 120-period MA
    df['ma_cross'] = (df['ma30'] > df['ma120']).astype(int)
    df['ma_cross_shift'] = df['ma_cross'].shift(1)
    df['golden_cross'] = (df['ma_cross'] == 1) & (df['ma_cross_shift'] == 0)
    cross_idx_list = df[df['golden_cross']].index.tolist()
    signal = len(cross_idx_list) > 0

    # Detect volume surge: z-score of volume > 2.5
    df['vol_ma60'] = df['volume'].rolling(window=60).mean()
    df['vol_std60'] = df['volume'].rolling(window=60).std()
    df['z_score'] = (df['volume'] - df['vol_ma60']) / df['vol_std60']
    df['z_score'] = df['z_score'].fillna(0)
    surge_idx_list = df[df['z_score'] > 2.5].index.tolist()
    vol_surge = len(surge_idx_list) > 0

    if signal or vol_surge:
        print(f"✅ Signal Detected! signal: {signal}, vol_surge: {vol_surge}")

        if signal:
            idx = cross_idx_list[0]
            start = max(idx - 4, 0)
            print(f"First golden cross detected at index: {idx}")
            print(df.iloc[start:idx+1][["datetime", "close", "ma30", "ma120"]])

        if vol_surge:
            idx = surge_idx_list[0]
            start = max(idx - 4, 0)
            print(f"First surge detected at index: {idx}")
            print(df.iloc[start:idx+1][["datetime", "volume", "z_score", "vol_ma60", "vol_std60"]])

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Training job should be started',
                'golden_cross': bool(signal),
                'volume_surge': bool(vol_surge)
            })
        }
    else:
        print("No signal detected.")
        return {
            'statusCode': 200,
            'body': json.dumps('No signal detected')
        }
