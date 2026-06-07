variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "Região principal do deploy na AWS"
}

variable "project_name" {
  type        = string
  default     = "p2c-olist-lakehouse"
  description = "Nome base que será usado como prefixo nos recursos"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Ambiente de deployment (dev, staging, prod)"
}
