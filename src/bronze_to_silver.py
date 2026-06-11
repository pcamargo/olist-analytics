import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, to_timestamp, current_timestamp

def transform_orders(df):
    return df \
        .withColumn("order_purchase_timestamp", to_timestamp(col("order_purchase_timestamp"))) \
        .withColumn("order_approved_at", to_timestamp(col("order_approved_at"))) \
        .withColumn("order_delivered_carrier_date", to_timestamp(col("order_delivered_carrier_date"))) \
        .withColumn("order_delivered_customer_date", to_timestamp(col("order_delivered_customer_date"))) \
        .withColumn("order_estimated_delivery_date", to_timestamp(col("order_estimated_delivery_date"))) \
        .withColumn("ingestion_at", current_timestamp())  # Linhagem de dados (Audit column)

def transform_items(df):
    return df \
        .withColumn("shipping_limit_date", to_timestamp(col("shipping_limit_date"))) \
        .withColumn("price", col("price").cast("double")) \
        .withColumn("freight_value", col("freight_value").cast("double")) \
        .withColumn("ingestion_at", current_timestamp())

if __name__ == '__main__':
    # Inicialização obrigatória do contexto do Glue
    args = getResolvedOptions(sys.argv, ['JOB_NAME', 'DATA_LAKE_BUCKET'])
    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session

    job = Job(glueContext)
    job.init(args['JOB_NAME'], args)

    bucket_name = args['DATA_LAKE_BUCKET']

    print("Iniciando o processamento da tabela Orders...")

    # Leitura dos dados brutos (Bronze)
    orders_df = spark.read.format("csv") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load(f"s3://{bucket_name}/bronze/olist_orders_dataset.csv")

    # Transformações: Padronização de tipos de dados (Strings para Timestamp)
    orders_silver = transform_orders(orders_df)

    # Escrita na camada Silver em formato Parquet
    # Como pedidos possuem datas, podemos particionar por ano/mês da compra para otimizar custos no Athena
    orders_silver.write.format("parquet") \
        .mode("overwrite") \
        .save(f"s3://{bucket_name}/silver/orders/")


    # ==============================================================================
    # 2. PROCESSAMENTO DA TABELA: ORDER ITEMS (ITENS DOS PEDIDOS)
    # ==============================================================================
    print("Iniciando o processamento da tabela Order Items...")

    # Leitura dos dados brutos
    items_df = spark.read.format("csv") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load(f"s3://{bucket_name}/bronze/olist_order_items_dataset.csv")

    # Transformações: Ajustando tipagem de floats e timestamps
    items_silver = transform_items(items_df)

    # Escrita na camada Silver em formato Parquet
    items_silver.write.format("parquet") \
        .mode("overwrite") \
        .save(f"s3://{bucket_name}/silver/order_items/")

    #####
    # ==============================================================================
    # 3. PROCESSAMENTO DA TABELA: PRODUTOS
    # ==============================================================================
    print("Iniciando o processamento da tabela Products...")

    # Leitura dos dados brutos
    products_df = spark.read.format("csv") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load(f"s3://{bucket_name}/bronze/olist_products_dataset.csv")

    # Escrita na camada Silver em formato Parquet
    products_df.write.format("parquet") \
        .mode("overwrite") \
        .save(f"s3://{bucket_name}/silver/products/")

    print("Job Bronze to Silver concluído com sucesso!")
    job.commit()
