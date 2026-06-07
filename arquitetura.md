## Camada de Ingestão e Armazenamento (S3 Data Lake)
Criar um bucket S3 centralizado e estruturado sob o conceito de medalhão (Lakehouse architecture):

s3://seu-datalake-olist/bronze/ (Raw): Onde os arquivos originais (CSV) da Olist serão armazenados exatamente como vêm da fonte. Você pode simular a ingestão usando um script simples em Python (boto3) ou um AWS Lambda que busca os arquivos e faz o upload para este bucket.

s3://seu-datalake-olist/silver/ (Trusted): Dados limpos, com tipos de dados corrigidos (ex: colunas de data que eram strings convertidas para datetime), remoção de duplicatas e armazenados no formato colunar otimizado Parquet.

s3://seu-datalake-olist/gold/ (Refined): Dados agregados e modelados. Aqui você aplicará técnicas de modelagem dimensional (tabelas Fato e Dimensão, como Fato_Vendas, Dim_Clientes, Dim_Produtos) prontas para análises de negócio de alto desempenho.

## Camada de Computação e Processamento (AWS Glue & Spark)
Desenvolver os scripts de transformação em PySpark rodando no AWS Glue (Serverless Spark).

Job 1 (Bronze para Silver): Lê os múltiplos CSVs da camada Bronze, aplica tipagem estrita, trata valores nulos, realiza o particionamento (ex: particionar por ano/mês do pedido) e salva em Parquet na camada Silver.

Job 2 (Silver para Gold): Faz os cruzamentos relacionais de negócio (JOINS) entre as tabelas (Pedidos ➡️ Clientes ➡️ Pagamentos) para gerar as tabelas consolidadas da camada Gold.

## Camada de Catálogo, Governança e Consumo (Glue Crawler & Athena)
AWS Glue Data Catalog: Funcionará como o seu catálogo central de metadados.

AWS Glue Crawlers: Automatizados via Terraform para escanear as partições criadas nas camadas Silver e Gold, criando automaticamente o esquema das tabelas no catálogo.

Amazon Athena: Onde a mágica do consumo acontece. Você usará o Athena para rodar queries SQL de alta performance direto nos dados estruturados no S3.
