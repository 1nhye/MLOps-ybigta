terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ─────────────────────────────────────────────
# Module 호출
# ─────────────────────────────────────────────

module "s3" {
  source      = "./modules/s3"
  bucket_name = var.s3_bucket_name
  project     = var.project_name
}

module "cloudwatch" {
  source              = "./modules/cloudwatch"
  lambda_function_name = var.lambda_function_name
  retention_days      = var.cloudwatch_log_retention_days
}

module "iam" {
  source                  = "./modules/iam"
  project                 = var.project_name
  aws_region              = var.aws_region
  s3_bucket_name          = var.s3_bucket_name
  sagemaker_output_bucket = var.sagemaker_output_bucket
  lambda_function_name    = var.lambda_function_name
  log_group_arn           = module.cloudwatch.log_group_arn
}

module "lambda" {
  source               = "./modules/lambda"
  function_name        = var.lambda_function_name
  source_path          = var.lambda_source_path
  role_arn             = module.iam.lambda_role_arn
  pandas_layer_arn     = var.pandas_layer_arn
  timeout              = var.lambda_timeout
  memory_size          = var.lambda_memory_size
  s3_bucket_name       = var.s3_bucket_name
  log_group_name       = module.cloudwatch.log_group_name

  depends_on = [module.cloudwatch, module.iam]
}

module "eventbridge" {
  source               = "./modules/eventbridge"
  project              = var.project_name
  schedule_expression  = var.eventbridge_schedule_expression
  lambda_function_arn  = module.lambda.function_arn
  lambda_function_name = var.lambda_function_name

  depends_on = [module.lambda]
}
