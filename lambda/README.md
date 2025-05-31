# AWS Lambda & EventBridge Setup Guide

This guide explains how to set up AWS Lambda functions and EventBridge to build an automated MLOps pipeline.

## 📋 Table of Contents

- [AWS Lambda Setup](#aws-lambda-setup)
- [IAM Role Creation](#iam-role-creation)
- [Lambda Layer Addition](#lambda-layer-addition)
- [AWS EventBridge Setup](#aws-eventbridge-setup)

---

## 🚀 AWS Lambda Setup

### 1. Create Lambda Function

1. Click the **"Create function"** button in the AWS Lambda console.

   ![Lambda Function Creation](../assets/lambda/lambda-function.png)

### 2. Deploy Code

1. Navigate to the **Code source** section of your Lambda function.

   ![Lambda Code](../assets/lambda/lambda-code.png)

2. Copy the contents of the `signal.py` file and paste it into the Code source.
3. Click the **"Deploy"** button or press `Ctrl+Shift+U` to deploy.

---

## 🔐 IAM Role Creation

### 1. IAM Role Setup

1. Navigate to **IAM > Access management > Roles**.
2. Click the **"Create role"** button.

   ![Lambda IAM](../assets/lambda/lambda-IAM.png)

### 2. Permission Policy Configuration

Use the following JSON policy to set up the required permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "logs:CreateLogGroup",
      "Resource": "arn:aws:logs:<YOUR_REGION>:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:<YOUR_REGION>:/aws/lambda/<LAMBDA_FUNCTION_NAME>:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::<LAMBDA_FUNCTION_NAME>",
        "arn:aws:s3:::<LAMBDA_FUNCTION_NAME>/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::<SAGEMAKER_OUTPUT>",
        "arn:aws:s3:::<SAGEMAKER_OUTPUT>/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "sagemaker:CreateTrainingJob",
        "sagemaker:DescribeTrainingJob",
        "sagemaker:CreateModel",
        "sagemaker:CreateEndpointConfig",
        "sagemaker:CreateEndpoint",
        "sagemaker:InvokeEndpoint"
      ],
      "Resource": "*"
    }
  ]
}
```

> ⚠️ **Warning**: Replace `<YOUR_REGION>`, `<LAMBDA_FUNCTION_NAME>`, and `<SAGEMAKER_OUTPUT>` with actual values.

---

## 📦 Lambda Layer Addition

### 1. Create Pandas Layer (In EC2 or Linux environment)

```bash
mkdir python
pip install pandas -t python/
zip -r pandas_layer.zip python
```

### 2. Add Layer

1. Click the **"Add a layer"** button in the **Layers** section of your Lambda function.
2. Select `AWSSDKPandas-Python313` from **AWS layers** and click **Add**.

### 3. Edit Configuration

Edit the Lambda function configuration as needed.

![Lambda Configuration](../assets/lambda/lambda-configuration.png)

---

## ⏰ AWS EventBridge Setup

### 1. Schedule Registration

1. Create a new schedule in the EventBridge console.

   ![EventBridge Schedule](../assets/eventbridge/eventbridge-schedule.png)

2. Set up the CRON expression.

   ![EventBridge CRON](../assets/eventbridge/eventbridge-cron.png)

   **CRON Expression**: `0 0,4,8,12,16,20 * * ? *`
   
   > 📅 This expression runs daily at 0:00, 4:00, 8:00, 12:00, 16:00, and 20:00.

### 2. EventBridge IAM Role Registration

Set up the following policy to allow EventBridge to invoke Lambda functions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": [
                "arn:aws:lambda:<YOUR_REGION>:function:<LAMBDA_FUNCTION>:*",
                "arn:aws:lambda:<YOUR_REGION>:function:<LAMBDA_FUNCTION>"
            ]
        }
    ]
}
```

> ⚠️ **Warning**: Replace `<YOUR_REGION>` and `<LAMBDA_FUNCTION>` with actual values.

---

## 🎯 Complete!

Your AWS Lambda function will now automatically execute according to the EventBridge schedule to manage your MLOps pipeline.

### Next Steps

- Monitor Lambda function execution logs in CloudWatch Logs.
- Adjust the schedule as needed.
- Consider setting up error handling and notifications.