output "lambda_role_arn" {
  description = "Lambda 실행 역할 ARN"
  value       = aws_iam_role.lambda.arn
}

output "sagemaker_role_arn" {
  description = "SageMaker 실행 역할 ARN"
  value       = aws_iam_role.sagemaker.arn
}

output "eventbridge_role_arn" {
  description = "EventBridge 스케줄러 역할 ARN"
  value       = aws_iam_role.eventbridge.arn
}
