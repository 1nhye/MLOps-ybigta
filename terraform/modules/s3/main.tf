resource "aws_s3_bucket" "main" {
  bucket = var.bucket_name

  tags = {
    Project     = var.project
    ManagedBy   = "terraform"
  }
}

# 퍼블릭 액세스 차단 (보안 기본값)
resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.main.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 버전 관리 비활성화 (원시 데이터 스트림 — 덮어쓰기 없으므로 불필요)
resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id

  versioning_configuration {
    status = "Disabled"
  }
}

# 라이프사이클: 수집 데이터 90일 후 자동 삭제 (비용 최적화)
resource "aws_s3_bucket_lifecycle_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    id     = "expire-raw-topic-data"
    status = "Enabled"

    filter {
      prefix = "topics/"
    }

    expiration {
      days = 90
    }
  }

  rule {
    id     = "expire-model-artifacts"
    status = "Enabled"

    filter {
      prefix = "models/"
    }

    # 모델은 30개 버전까지 보관
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}
