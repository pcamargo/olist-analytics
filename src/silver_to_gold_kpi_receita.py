import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, date_format, sum, count, current_timestamp


def transform_orders(df):
    return df \
        .filter(col("order_status").isin("delivered", "shipped")) \
        .filter(col("order_approved_at").isNotNull()) \
        .withColumn("year_month", date_format(col("order_approved_at"), "yyyy-MM"))

if __name__ == "__main__":
    args = getResolvedOptions(sys.argv, ['JOB_NAME', 'DATA_LAKE_BUCKET'])
    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session
    job = Job(glueContext)
    job.init(args['JOB_NAME'], args)

    bucket_name = args['DATA_LAKE_BUCKET']

    # 1. LEITURA DA CAMADA SILVER
    orders_df = spark.read.format("parquet").load(f"s3://{bucket_name}/silver/orders/")
    order_items_df = spark.read.format("parquet").load(f"s3://{bucket_name}/silver/order_items/")

    # 2. TRANSFORMAÇÃO E AGREGAÇÃO (Regra de Negócio do KPI)
    # Filtrar pedidos válidos e extrair Ano-Mês
    valid_orders = transform_orders(order_items_df)

    # Juntar com os itens para somar os valores
    kpi_receita_mensal = valid_orders.join(order_items_df, "order_id", "inner") \
        .groupBy("year_month") \
        .agg(
            sum("price").alias("total_revenue"),
            sum("freight_value").alias("total_freight"),
            count("order_id").distinct().alias("total_orders")
        ) \
        .withColumn("calculated_at", current_timestamp()) \
        .orderBy("year_month")

    # 3. ESCRITA NA CAMADA GOLD
    # Salva em formato Parquet para máxima performance de leitura no Athena
    kpi_receita_mensal.write \
        .format("parquet") \
        .mode("overwrite") \
        .save(f"s3://{bucket_name}/gold/kpi_monthly_revenue/")

    job.commit()
