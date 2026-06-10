import pytest
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType, LongType
from src.silver_to_gold_kpi_receita import transform_orders


# Cria uma sessão local do Spark que roda em memória para o teste
@pytest.fixture(scope="session")
def spark_fixture():
    return SparkSession.builder \
        .master("local[*]") \
        .appName("testing-pyspark-kpi-locally") \
        .getOrCreate()


def test_transform_orders_filters_valid_status(spark_fixture):
    # 1. Dado (Given): Dados de entrada mockados com diferentes status
    input_data = [
        (
            "order_001",
            "delivered",
            "2026-06-01 10:00:00",
        ),
        (
            "order_002",
            "shipped",
            "2026-06-02 14:30:00",
        ),
        (
            "order_003",
            "cancelled",
            "2026-06-03 08:15:00",
        ),
        (
            "order_004",
            "pending",
            "2026-06-04 16:45:00",
        )
    ]
    schema = [
        "order_id",
        "order_status",
        "order_approved_at"
    ]
    df_input = spark_fixture.createDataFrame(input_data, schema)

    # 2. Quando (When): Executamos a nossa função de transformação
    df_output = transform_orders(df_input)

    # 3. Então (Then): Validamos se o resultado é o esperado
    result = df_output.collect()
    
    # Verifica se apenas os status válidos (delivered, shipped) foram mantidos
    assert len(result) == 2
    assert result[0]["order_id"] == "order_001"
    assert result[1]["order_id"] == "order_002"


def test_transform_orders_filters_null_approved_at(spark_fixture):
    # 1. Dado (Given): Dados com alguns order_approved_at nulos
    input_data = [
        (
            "order_001",
            "delivered",
            "2026-06-01 10:00:00",
        ),
        (
            "order_002",
            "delivered",
            None,
        ),
        (
            "order_003",
            "shipped",
            "2026-06-03 14:30:00",
        )
    ]
    schema = [
        "order_id",
        "order_status",
        "order_approved_at"
    ]
    df_input = spark_fixture.createDataFrame(input_data, schema)

    # 2. Quando (When): Executamos a nossa função de transformação
    df_output = transform_orders(df_input)

    # 3. Então (Then): Validamos se o resultado é o esperado
    result = df_output.collect()
    
    # Verifica se apenas registros com order_approved_at não-nulo foram mantidos
    assert len(result) == 2
    # Verifica se nenhum valor nulo está presente
    assert all(row["order_approved_at"] is not None for row in result)


def test_transform_orders_creates_year_month_column(spark_fixture):
    # 1. Dado (Given): Dados de entrada com timestamps em diferentes meses
    input_data = [
        (
            "order_001",
            "delivered",
            "2026-06-01 10:00:00",
        ),
        (
            "order_002",
            "shipped",
            "2026-06-15 14:30:00",
        ),
        (
            "order_003",
            "delivered",
            "2026-07-05 08:15:00",
        )
    ]
    schema = [
        "order_id",
        "order_status",
        "order_approved_at"
    ]
    df_input = spark_fixture.createDataFrame(input_data, schema)

    # 2. Quando (When): Executamos a nossa função de transformação
    df_output = transform_orders(df_input)

    # 3. Então (Then): Validamos se o resultado é o esperado
    result = df_output.collect()
    
    # Verifica se a coluna 'year_month' foi criada
    assert "year_month" in df_output.columns
    # Verifica se os valores de year_month estão corretos
    assert result[0]["year_month"] == "2026-06"
    assert result[1]["year_month"] == "2026-06"
    assert result[2]["year_month"] == "2026-07"


def test_transform_orders_combined_filters(spark_fixture):
    # 1. Dado (Given): Dados que testam todos os filtros juntos
    input_data = [
        (
            "order_001",
            "delivered",
            "2026-06-01 10:00:00",
        ),
        (
            "order_002",
            "pending",
            "2026-06-02 14:30:00",
        ),
        (
            "order_003",
            "shipped",
            None,
        ),
        (
            "order_004",
            "shipped",
            "2026-06-04 16:45:00",
        )
    ]
    schema = [
        "order_id",
        "order_status",
        "order_approved_at"
    ]
    df_input = spark_fixture.createDataFrame(input_data, schema)

    # 2. Quando (When): Executamos a nossa função de transformação
    df_output = transform_orders(df_input)

    # 3. Então (Then): Validamos se o resultado é o esperado
    result = df_output.collect()
    
    # Verifica se apenas os registros que passaram em TODOS os filtros foram mantidos
    assert len(result) == 2
    assert result[0]["order_id"] == "order_001"
    assert result[1]["order_id"] == "order_004"
    # Verifica se a coluna year_month foi criada para os registros válidos
    assert result[0]["year_month"] == "2026-06"
    assert result[1]["year_month"] == "2026-06"
