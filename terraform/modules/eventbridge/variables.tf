variable "project" {
  description = "프로젝트 이름"
  type        = string
}

variable "schedule_expression" {
  description = "EventBridge cron 표현식"
  type        = string
}

variable "lambda_function_arn" {
  description = "타겟 Lambda 함수 ARN"
  type        = string
}

variable "lambda_function_name" {
  description = "타겟 Lambda 함수 이름"
  type        = string
}
