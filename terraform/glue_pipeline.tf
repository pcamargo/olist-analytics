# ==============================================================================
# 1. UPLOAD AUTOMÁTICO DOS SCRIPTS PYSPARK PARA O S3
# ==============================================================================

resource "aws_s3_object" "script_bronze_to_silver" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "scripts/bronze_to_silver.py"
  source = "../src/glue_jobs/bronze_to_silver.py"
  etag   = filemd5("../src/glue_jobs/bronze_to_silver.py") # Força o update do job na AWS caso o código mude localmente
}

resource "aws_s3_object" "script_silver_to_gold" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "scripts/silver_to_gold.py"
  source = "../src/glue_jobs/silver_to_gold.py"
  etag   = filemd5("../src/glue_jobs/silver_to_gold.py")
}

# ==============================================================================
# 2. DEFINIÇÃO DOS AWS GLUE JOBS (PROCESSAMENTO SERVERLESS)
# ==============================================================================

resource "aws_glue_job" "bronze_to_silver" {
  name              = "${var.project_name}-${var.environment}-bronze-to-silver"
  role_arn          = aws_iam_role.glue_service_role.arn
  glue_version      = "4.0" # Versão moderna suportando Spark 3.3 e Python 3
  worker_type       = "G.1X"
  number_of_workers = 2     # Configuração econômica para dev/portfólio

  timeout           = 10
  execution_class   = "FLEX"

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.data_lake.bucket}/${aws_s3_object.script_bronze_to_silver.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--continuous-log-logGroup"          = "/aws-glue/jobs"
    "--enable-continuous-cloudwatch-log" = "true"
    "--job-language"                     = "python"
    # Passa o nome do bucket dinamicamente para o script PySpark
    "--DATA_LAKE_BUCKET"                 = aws_s3_bucket.data_lake.bucket
  }
}

resource "aws_glue_job" "silver_to_gold" {
  name              = "${var.project_name}-${var.environment}-silver-to-gold"
  role_arn          = aws_iam_role.glue_service_role.arn
  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2

  timeout           = 10
  execution_class   = "FLEX"

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.data_lake.bucket}/${aws_s3_object.script_silver_to_gold.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--continuous-log-logGroup"          = "/aws-glue/jobs"
    "--enable-continuous-cloudwatch-log" = "true"
    "--job-language"                     = "python"
    "--DATA_LAKE_BUCKET"                 = aws_s3_bucket.data_lake.bucket
  }
}

# ==============================================================================
# 3. AWS GLUE CRAWLERS (GOVERNANÇA E ESQUEMA AUTOMÁTICO PARA O ATHENA)
# ==============================================================================

# Crawler para a camada Gold (Onde geramos a Fato e a Dimensão)
resource "aws_glue_crawler" "gold_crawler" {
  database_name = aws_glue_catalog_database.olist_db.name
  name          = "${var.project_name}-${var.environment}-gold-crawler"
  role          = aws_iam_role.glue_service_role.arn

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}/gold/"
  }

  # Configuração crucial para performance: Atualiza e mapeia novas partições adicionadas na Gold
  configuration = jsonencode({
    Version = 1.0
    CrawlerOutput = {
      Partitions = { AddOrUpdateBehavior = "InheritFromTable" }
    }
  })
}
