### Data Engineering em AWS

https://www.kaggle.com/code/leandroal/an-lise-do-e-commerce-no-brasil-olist-dataset


Plataforma de Dados Moderna e Escalável. Vamos recapitular o nível de maturidade do seu repositório atual:

Camada de Dados Otimizada: Arquitetura Medalhão estruturada no S3 com armazenamento em formato colunar (Parquet), compactação eficiente e estratégia de particionamento temporal.

Infraestrutura como Código (IaC): Tudo criado via Terraform, com destruição e criação limpa, sem dependência de cliques manuais no console da AWS.

Segurança de Elite (SecOps): Princípio do menor privilégio aplicado nas políticas do IAM, isolamento do escopo do PassRole, e eliminação de chaves estáticas no GitHub graças ao AWS OIDC.

Práticas de Engenharia de Software (DataOps): Testes unitários rodando em memória com PyTest + PySpark, validação sintática automatizada via lint do Terraform, e cache inteligente para acelerar o CI/CD.

FinOps (Eficiência de Custo): Consultas otimizadas via particionamento no Athena e custos de computação serverless minimizados com o Glue Flex.