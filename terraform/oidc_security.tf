# ==============================================================================
# 1. CONFIGURAÇÃO DO PROVEDOR OIDC DO GITHUB NA AWS
# ==============================================================================
resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  # Thumbprint oficial do certificado do GitHub Actions
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1", "1c58a3a8518e8759bf075b76b750d4f2df264fcd"]
}

# ==============================================================================
# 2. ROLE QUE O GITHUB ACTIONS VAI ASSUMIR DINAMICAMENTE
# ==============================================================================
resource "aws_iam_role" "github_actions_oidc_role" {
  name = "${var.project_name}-${var.environment}-github-actions-oidc-role"

  # Política de Confiança: Permite APENAS o seu repositório específico assumir esta Role
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "allow"
        Action = "sts:AssumeRoleWithWebIdentity"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        }
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            # ⚠️ IMPORTANTE: Substitua 'seu-usuario-github/seu-repositorio' pelo seu caminho real
            "token.actions.githubusercontent.com:sub" = "repo:pcamargo/olist-analytics:*"
          }
        }
      }
    ]
  })
}

# ==============================================================================
# 3. ANEXAR A POLÍTICA DE PERMISSÕES DO PIPELINE À NOVA ROLE OIDC
# ==============================================================================
# Aqui você anexa aquela política com menor privilégio que corrigimos anteriormente
resource "aws_iam_role_policy_attachment" "github_actions_attach" {
  role       = aws_iam_role.github_actions_oidc_role.name
  policy_arn = "arn:aws:iam::846251877823:policy/github-actions-policy-deploy"
}

output "github_actions_role_arn" {
  value       = aws_iam_role.github_actions_oidc_role.arn
  description = "Copie este ARN para colocar no seu arquivo deploy.yml"
}
