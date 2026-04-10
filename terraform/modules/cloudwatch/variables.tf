variable "lambda_function_name" {
  description = "Lambda 함수 이름"
  type        = string
}

variable "retention_days" {
  description = "로그 보존 기간 (일)"
  type        = number
  default     = 30
}
