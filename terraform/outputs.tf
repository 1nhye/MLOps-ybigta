output "s3_bucket_name" {
  description = "생성된 S3 버킷 이름"
  value       = module.s3.bucket_name
}

output "s3_bucket_arn" {
  description = "생성된 S3 버킷 ARN"
  value       = module.s3.bucket_arn
}

output "lambda_function_name" {
  description = "생성된 Lambda 함수 이름"
  value       = module.lambda.function_name
}

output "lambda_function_arn" {
  description = "생성된 Lambda 함수 ARN"
  value       = module.lambda.function_arn
}

output "lambda_role_arn" {
  description = "Lambda 실행 IAM 역할 ARN"
  value       = module.iam.lambda_role_arn
}

output "sagemaker_role_arn" {
  description = "SageMaker 실행 IAM 역할 ARN (signal.py에 주입 필요)"
  value       = module.iam.sagemaker_role_arn
}

output "eventbridge_schedule_arn" {
  description = "생성된 EventBridge 스케줄 ARN"
  value       = module.eventbridge.schedule_arn
}

output "cloudwatch_log_group_name" {
  description = "Lambda 로그 그룹 이름"
  value       = module.cloudwatch.log_group_name
}
