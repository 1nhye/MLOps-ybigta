data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# IAM role for EventBridge Scheduler to invoke Lambda
data "aws_iam_role" "eventbridge" {
  name = "${var.project}-eventbridge-role"
}

resource "aws_scheduler_schedule" "btc_signal" {
  name        = "${var.project}-btc-signal-schedule"
  description = "비트코인 신호 감지 Lambda를 하루 6회 실행 (KST 0, 4, 8, 12, 16, 20시)"

  # UTC 기준 cron: KST는 UTC+9이므로 -9시간 적용
  # KST 0,4,8,12,16,20 → UTC 15,19,23,3,7,11
  schedule_expression          = var.schedule_expression
  schedule_expression_timezone = "Asia/Seoul"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = var.lambda_function_arn
    role_arn = data.aws_iam_role.eventbridge.arn

    # Lambda 호출 실패 시 재시도 설정
    retry_policy {
      maximum_retry_attempts       = 2
      maximum_event_age_in_seconds = 3600
    }
  }
}
