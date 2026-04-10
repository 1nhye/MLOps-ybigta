variable "project" {
  description = "프로젝트 이름"
  type        = string
}

variable "aws_region" {
  description = "AWS 리전"
  type        = string
}

variable "s3_bucket_name" {
  description = "데이터 S3 버킷 이름"
  type        = string
}

variable "sagemaker_output_bucket" {
  description = "SageMaker 결과물 저장 버킷"
  type        = string
}

variable "lambda_function_name" {
  description = "Lambda 함수 이름"
  type        = string
}

variable "log_group_arn" {
  description = "Lambda CloudWatch 로그 그룹 ARN"
  type        = string
}
