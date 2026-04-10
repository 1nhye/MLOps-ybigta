# signal.py를 zip으로 패키징
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../../${var.source_path}"
  output_path = "${path.module}/../../.terraform/lambda_package.zip"
}

resource "aws_lambda_function" "signal_detector" {
  function_name    = var.function_name
  description      = "비트코인 시장 신호 감지 (Golden Cross / Volume Surge) 및 SageMaker 학습 트리거"
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  role        = var.role_arn
  handler     = "signal.lambda_handler"
  runtime     = "python3.13"
  timeout     = var.timeout
  memory_size = var.memory_size

  # AWSSDKPandas 관리형 레이어 연결
  layers = [var.pandas_layer_arn]

  # 환경변수로 S3 버킷 이름 주입 (signal.py의 하드코딩 대체)
  environment {
    variables = {
      BUCKET_NAME       = var.s3_bucket_name
      LOG_GROUP_NAME    = var.log_group_name
    }
  }

  # 로그 그룹이 먼저 생성된 후 함수 배포
  depends_on = [var.log_group_name]

  tags = {
    ManagedBy = "terraform"
  }
}

# EventBridge Scheduler가 Lambda를 호출할 수 있도록 권한 부여
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridgeScheduler"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.signal_detector.function_name
  principal     = "scheduler.amazonaws.com"
}
