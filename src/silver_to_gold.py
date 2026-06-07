import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, year, month, current_timestamp

# Inicialização do contexto do Glue
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'DATA_LAKE_BUCKET'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

bucket_name = args['DATA_LAKE_BUCKET']

# Caminhos das camadas S3
silver_path = f"s3://{bucket_name}/silver"
gold_path = f"s3://{bucket_name}/gold"

# ==============================================================================
# 1. LEITURA DOS DADOS DA CAMADA SILVER (FORMATO PARQUET)
# ==============================================================================
print("Lendo os dados consolidados da camada Silver...")

df_orders = spark.read.parquet(f"{silver_path}/orders/")
df_items = spark.read.parquet(f"{silver_path}/order_items/")

# ==============================================================================
# 2. CONSTRUÇÃO DA TABELA DIM_CLIENTES (Exemplo de Dimensão)
# ==============================================================================
# Nota: No dataset completo da Olist, existe uma tabela específica de clientes.
# Para este pipeline, vamos extrair os IDs e criar atributos únicos de auditoria.
print("Construindo a Dim_Clientes...")

dim_clientes = df_orders.select("customer_id").distinct() \
    .withColumn("dw_updated_at", current_timestamp())

# Escrita da Dimensão na Gold
dim_clientes.write.format("parquet") \
    .mode("overwrite") \
    .save(f"{gold_path}/dim_clientes/")

# ==============================================================================
# 3. CONSTRUÇÃO DA TABELA FATO_VENDAS (Cruzamento e Modelagem)
# ==============================================================================
print("Construindo a Fato_Vendas através de JOINS...")

# Unindo os cabeçalhos dos pedidos (Orders) com as linhas de itens (Order Items)
# Usando inner join para garantir consistência analítica
fato_vendas = df_orders.join(df_items, on="order_id", how="inner")

# Seleção e renomeação de colunas estratégicas para o negócio
fato_vendas_final = fato_vendas.select(
    col("order_id").alias("sk_order"),
    col("customer_id").alias("nk_customer"),
    col("order_status"),
    col("order_purchase_timestamp"),
    col("product_id").alias("nk_product"),
    col("seller_id").alias("nk_seller"),
    col("price"),
    col("freight_value"),
    # Criando colunas de partição baseadas na data de compra
    year(col("order_purchase_timestamp")).alias("year_purchase"),
    month(col("order_purchase_timestamp")).alias("month_purchase"),
    current_timestamp().alias("dw_created_at")
)

# ==============================================================================
# 4. ESCRITA OTIMIZADA (PARTICIONAMENTO)
# ==============================================================================
print("Gravando a Fato_Vendas na Gold com particionamento por Ano e Mês...")

# Particionar por Ano/Mês de compra é crucial. Quando o analista rodar uma query no
# Athena filtrando um mês específico, o Athena lerá APENAS aquela pasta no S3,
# reduzindo drasticamente o custo por query (pago por TB escaneado).
fato_vendas_final.write.format("parquet") \
    .mode("overwrite") \
    .partitionBy("year_purchase", "month_purchase") \
    .save(f"{gold_path}/fato_vendas/")

print("Job Silver to Gold concluído com sucesso!")
job.commit()
