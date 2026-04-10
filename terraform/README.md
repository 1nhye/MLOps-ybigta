# Terraform — AWS 인프라 자동화

이 디렉토리는 MLOps 파이프라인에 필요한 AWS 리소스를 코드로 관리합니다.

## 관리 리소스

| 모듈 | AWS 리소스 | 설명 |
|------|-----------|------|
| `modules/s3` | S3 Bucket | 수집 데이터 + 모델 저장소 |
| `modules/iam` | IAM Role × 3 | Lambda / SageMaker / EventBridge 실행 역할 |
| `modules/cloudwatch` | Log Group | Lambda 로그, 30일 보존 |
| `modules/lambda` | Lambda Function | 신호 감지 함수 (`signal.py`) |
| `modules/eventbridge` | Scheduler | 하루 6회 자동 실행 (KST 기준) |

## 사전 준비

```bash
# Terraform 설치 (>= 1.5.0)
brew install terraform          # macOS
# 또는 https://developer.hashicorp.com/terraform/downloads

# AWS 자격증명 설정
aws configure
# AWS Access Key ID, Secret Access Key, 리전(ap-northeast-2) 입력
```

## 실행 방법

```bash
cd terraform

# 1. 초기화 (provider 및 모듈 다운로드)
terraform init

# 2. 변경 사항 미리보기
terraform plan

# 3. 실제 적용
terraform apply
```

## 주요 변수

`variables.tf`에서 아래 값을 확인·수정하세요.

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `aws_region` | `ap-northeast-2` | AWS 리전 |
| `s3_bucket_name` | `ybigta-crypto-price` | S3 버킷 이름 |
| `lambda_function_name` | `btc-signal-detector` | Lambda 함수 이름 |
| `pandas_layer_arn` | `...Python313:15` | AWSSDKPandas Layer ARN **★ 교체 필요** |
| `cloudwatch_log_retention_days` | `30` | 로그 보존 기간 |
| `eventbridge_schedule_expression` | KST 0,4,8,12,16,20시 | 실행 스케줄 |

### AWSSDKPandas Layer ARN 확인 방법

```bash
aws lambda list-layers \
  --compatible-runtime python3.13 \
  --query "Layers[?contains(LayerName, 'AWSSDKPandas')].LatestMatchingVersion.LayerVersionArn" \
  --region ap-northeast-2
```

또는 [공식 문서](https://aws-sdk-pandas.readthedocs.io/en/stable/layers.html)에서 리전별 ARN 확인

## apply 후 출력값

```
s3_bucket_name            = "ybigta-crypto-price"
lambda_function_name      = "btc-signal-detector"
lambda_role_arn           = "arn:aws:iam::123456789:role/ybigta-btc-lambda-execution-role"
sagemaker_role_arn        = "arn:aws:iam::123456789:role/ybigta-btc-sagemaker-execution-role"
eventbridge_schedule_arn  = "arn:aws:scheduler:ap-northeast-2:..."
cloudwatch_log_group_name = "/aws/lambda/btc-signal-detector"
```

`sagemaker_role_arn` 출력값을 `lambda/signal.py`의 `SAGEMAKER_ROLE_ARN`에 사용하세요.

## 리소스 삭제

```bash
terraform destroy
```
