import json
import boto3
import pandas as pd
from datetime import datetime, timedelta, timezone

s3 = boto3.client('s3')
# sagemaker = boto3.client('sagemaker')

BUCKET_NAME = "ybigta-crypto-price"
PREFIX = 'topics/'
#TODO
# training docker image uri
# sagemaker role
# DOCKER_IMAGE_URI=
# SAGEMAKER_ROLE_ARN=

def lambda_handler(event, context):
    now = datetime.now(timezone.utc)
    past = now - timedelta(hours=4)

    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX)
    files = [
        obj["Key"] for obj in response.get("Contents", [])
        if past <= obj["LastModified"] <= now  
    ]

    if not files:
        return {
            'statusCode': 200,
            'body': json.dumps('No recent files to process')
        }

    dfs = []
    for file in sorted(files):
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=file)
        content = obj['Body'].read()
        df = pd.read_json(content, lines=True)
        dfs.append(df)

    print(f"Processed file: {file}")
    df = pd.concat(dfs, ignore_index=True).sort_values(by='timestamp')
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')

    # moving average
    df['ma30'] = df['close'].rolling(window=30).mean()
    df['ma120'] = df['close'].rolling(window=120).mean()

    # golden cross
    df['ma_cross'] = (df['ma30'] > df['ma120']).astype(int)
    df['ma_cross_shift'] = df['ma_cross'].shift(1)
    df['golden_cross'] = (df['ma_cross'] == 1) & (df['ma_cross_shift'] == 0)
    cross_idx_list = df[df['golden_cross']].index.tolist()
    signal = len(cross_idx_list) > 0

    # volumn surge
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
            'body': 'Training job should be started'
        }

    else:
        print("No signal detected.")
        return {
            'statusCode': 200,
            'body': 'No signal detected'
        }
