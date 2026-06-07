# Criação do assume role policy para o serviço do Glue
data "aws_iam_policy_document" "glue_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "glue_service_role" {
  name               = "${var.project_name}-${var.environment}-glue-role"
  assume_role_policy = data.aws_iam_policy_document.glue_assume_role.json
}

# Política customizada com privilégios limitados ao nosso Bucket e ao Catalog
resource "aws_iam_policy" "glue_custom_policy" {
  name        = "${var.project_name}-${var.environment}-glue-policy"
  description = "Acesso limitado para escrita/leitura do Data Lake Olist e CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.data_lake.arn}",
          "${aws_s3_bucket.data_lake.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "glue:*Database*",
          "glue:*Table*",
          "glue:*Partition*",
          "glue:BatchCreatePartition",
          "glue:BatchGetPartition"
        ]
        Resource = ["*"]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*:/aws-glue/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "glue_attach_custom" {
  role       = aws_iam_role.glue_service_role.name
  policy_arn = aws_iam_policy.glue_custom_policy.arn
}