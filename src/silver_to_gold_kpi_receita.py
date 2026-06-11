import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

from pyspark.sql.functions import col, rank, date_format, sum, count, countDistinct, current_timestamp
from pyspark.sql.window import Window

def transform_orders(df):
    return df \
        .filter(col("order_status").isin("delivered", "shipped")) \
        .filter(col("order_approved_at").isNotNull()) \
        .withColumn("year_month", date_format(col("order_approved_at"), "yyyy-MM"))

def save_as_parquet(df, table_name):
    # 3. ESCRITA NA CAMADA GOLD
    # Salva em formato Parquet para máxima performance de leitura no Athena
    df.write \
        .format("parquet") \
        .mode("overwrite") \
        .save(f"s3://{bucket_name}/gold/{table_name}/")

def kpi_receita_mensal(orders_df, order_items_df):
    # Juntar com os itens para somar os valores
    df = orders_df.join(order_items_df, "order_id", "inner") \
        .groupBy("year_month") \
        .agg(
        sum("price").alias("total_revenue"),
        sum("freight_value").alias("total_freight"),
        count("order_id").distinct().alias("total_orders")
    ) \
        .withColumn("calculated_at", current_timestamp()) \
        .orderBy("year_month")

    save_as_parquet(df, 'kpi_monthly_revenue')

def kpi_monthly_sales_performance(orders_df, order_items_df):
    df = orders_df.join(order_items_df, "order_id") \
        .groupBy("year_month") \
        .agg(
            sum("price").alias("total_revenue"),
            countDistinct("order_id").alias("total_orders"),
            count("product_id").alias("total_items_sold")
        ) \
        .withColumn("average_ticket", col("total_revenue") / col("total_orders"))

    save_as_parquet(df, 'kpi_monthly_sales_performance')

def kpi_top_sellers(orders_df, order_items_df):
    df = orders_df.join(order_items_df, "order_id") \
        .groupBy("year_month", "seller_id") \
        .agg(sum("price").alias("seller_revenue"), count("order_id").alias("orders_fulfilled"))

    window_spec = Window.partitionBy("year_month").orderBy(col("seller_revenue").desc())
    top_sellers = df.withColumn("rank_position", rank().over(window_spec)).filter(col("rank_position") <= 10)
    save_as_parquet(top_sellers, 'kpi_top_sellers')

def kpi_top_products(orders_df, order_items_df, products_df):
    # Juntar Pedidos -> Itens -> Detalhes do Produto
    joined_df = orders_df \
        .join(order_items_df, "order_id", "inner") \
        .join(products_df, "product_id", "inner")

    # Agrupar por mês e produto para calcular volume e receita por item
    aggregated_products = joined_df \
        .groupBy("year_month", "product_id", "product_category_name") \
        .agg(
            count("product_id").alias("units_sold"),
            sum("price").alias("product_revenue")
        )

    # Criar uma janela partcionada por MÊS e ordenada pela QUANTIDADE de unidades vendidas
    window_spec = Window.partitionBy("year_month").orderBy(col("units_sold").desc(), col("product_revenue").desc())

    # Aplicar o ranking e filtrar apenas os TOP 10 de cada mês
    top_products_gold = aggregated_products \
        .withColumn("product_rank", rank().over(window_spec)) \
        .filter(col("product_rank") <= 10) \
        .withColumn("calculated_at", current_timestamp()) \
        .orderBy("year_month", "product_rank")

    save_as_parquet(top_products_gold, 'kpi_top_products')

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
    products_df = spark.read.format("parquet").load(f"s3://{bucket_name}/silver/products/")

    # 2. TRANSFORMAÇÃO E AGREGAÇÃO (Regra de Negócio do KPI)
    # Filtrar pedidos válidos e extrair Ano-Mês
    valid_orders = transform_orders(order_items_df)

    kpi_receita_mensal(valid_orders, order_items_df)
    kpi_monthly_sales_performance(valid_orders, order_items_df)
    kpi_top_sellers(valid_orders, order_items_df)
    kpi_top_products(valid_orders, order_items_df, products_df)

    job.commit()
