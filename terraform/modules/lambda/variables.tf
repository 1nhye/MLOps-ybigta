variable "function_name" {
  description = "Lambda 함수 이름"
  type        = string
}

variable "source_path" {
  description = "signal.py 상대 경로 (terraform/ 기준)"
  type        = string
}

variable "role_arn" {
  description = "Lambda 실행 IAM 역할 ARN"
  type        = string
}

variable "pandas_layer_arn" {
  description = "AWSSDKPandas-Python313 레이어 ARN"
  type        = string
}

variable "timeout" {
  description = "타임아웃 (초)"
  type        = number
}

variable "memory_size" {
  description = "메모리 크기 (MB)"
  type        = number
}

variable "s3_bucket_name" {
  description = "데이터 S3 버킷 이름"
  type        = string
}

variable "log_group_name" {
  description = "CloudWatch 로그 그룹 이름"
  type        = string
}
