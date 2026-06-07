terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = var.project_name
      Env       = var.environment
      ManagedBy = "Terraform"
    }
  }
}

# 1. Bucket S3 para o Data Lake (Arquitetura Medalhão)
resource "aws_s3_bucket" "data_lake" {
  bucket        = "${var.project_name}-${var.environment}-storage"
  force_destroy = true # Facilita a limpeza do ambiente de testes
}

# Bloqueio de acesso público ao S3 (Best Practice de segurança)
resource "aws_s3_bucket_public_access_block" "data_lake_privacy" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Criptografia server-side por padrão
resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake_crypto" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Estrutura de pastas simulada no S3 (Bronze, Silver, Gold, Scripts)
resource "aws_s3_object" "lake_folders" {
  for_each = toset(["bronze/", "silver/", "gold/", "scripts/", "athena-results/"])
  bucket   = aws_s3_bucket.data_lake.id
  key      = each.value
}

# 2. AWS Glue Data Catalog Database
resource "aws_glue_catalog_database" "olist_db" {
  name = "${var.project_name}_${var.environment}_db"
}
