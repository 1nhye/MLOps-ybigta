variable "aws_region" {
  description = "AWS 리전"
  type        = string
  default     = "ap-northeast-2"
}

variable "project_name" {
  description = "프로젝트 이름 (리소스 이름 prefix로 사용)"
  type        = string
  default     = "ybigta-btc"
}

variable "s3_bucket_name" {
  description = "비트코인 데이터 및 모델 저장용 S3 버킷 이름"
  type        = string
  default     = "ybigta-crypto-price"
}

variable "lambda_function_name" {
  description = "신호 감지 Lambda 함수 이름"
  type        = string
  default     = "btc-signal-detector"
}

variable "lambda_source_path" {
  description = "Lambda 함수 소스 파일 경로 (signal.py)"
  type        = string
  default     = "../lambda/signal.py"
}

# AWSSDKPandas-Python313 레이어 ARN (리전마다 다름)
# ap-northeast-2 최신 ARN: https://aws-sdk-pandas.readthedocs.io/en/stable/layers.html 에서 확인
variable "pandas_layer_arn" {
  description = "AWSSDKPandas-Python313 Lambda Layer ARN"
  type        = string
  # 아래 값은 ap-northeast-2 기준 예시 — 실제 최신 버전으로 교체 필요
  default     = "arn:aws:lambda:ap-northeast-2:336392948345:layer:AWSSDKPandas-Python313:15"
}

variable "lambda_timeout" {
  description = "Lambda 함수 타임아웃 (초)"
  type        = number
  default     = 300
}

variable "lambda_memory_size" {
  description = "Lambda 함수 메모리 크기 (MB)"
  type        = number
  default     = 512
}

variable "cloudwatch_log_retention_days" {
  description = "CloudWatch 로그 보존 기간 (일)"
  type        = number
  default     = 30
}

variable "eventbridge_schedule_expression" {
  description = "EventBridge cron 표현식 (UTC 기준)"
  type        = string
  # KST 0, 4, 8, 12, 16, 20시 = UTC 15, 19, 23, 3, 7, 11시 전날/당일
  default     = "cron(0 15,19,23,3,7,11 * * ? *)"
}

variable "sagemaker_output_bucket" {
  description = "SageMaker 결과물 저장 S3 버킷 (학습 데이터와 동일 버킷 사용 가능)"
  type        = string
  default     = "ybigta-crypto-price"
}
