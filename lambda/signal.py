import json
import boto3
import pandas as pd
from datetime import datetime, timedelta, timezone

s3 = boto3.client('s3')
sagemaker = boto3.client('sagemaker')

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
    df = pd.concat(dfs, ignore_index=True)
    df = df.sort_values(by='timestamp')

    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')

    df['ma30'] = df['close'].rolling(window=30).mean()
    df['ma120'] = df['close'].rolling(window=120).mean()

    signal = (
        df['ma30'].iloc[-2] < df['ma120'].iloc[-2] and
        df['ma30'].iloc[-1] > df['ma120'].iloc[-1]
    )

    df['vol_ma60'] = df['volume'].rolling(window=60).mean()
    vol_surge = df['volume'].iloc[-1] > 3 * df['vol_ma60'].iloc[-1]

    if signal or vol_surge:
        print(f"Signal Detected! signal: {signal}, vol_surge: {vol_surge}")
        print(df.tail(5))
        return {
            'statusCode': 200,
            'body': f"Training job should be started"
        }
    else:
        return {
            'statusCode': 200,
            'body': 'No signal detected'
        }
