import pytest
from pyspark.sql import SparkSession
from src.bronze_to_silver import transform_orders


# Cria uma sessão local do Spark que roda em memória para o teste
@pytest.fixture(scope="session")
def spark_fixture():
    return SparkSession.builder \
        .master("local[*]") \
        .appName("testing-pyspark-locally") \
        .getOrCreate()


def test_transform_orders_converts_timestamps_correctly(spark_fixture):
    # 1. Dado (Given): Dados de entrada mockados (simulando o CSV bruto)
    input_data = [
        (
            "order_001",
            "2026-06-01 10:00:00",
            "2026-06-01 10:05:00",
            "2026-06-01 10:30:00",
            "2026-06-01 10:50:00",
            "2026-06-01 11:00:00"
        ),
        (
            "order_002",
            "2026-06-02 14:30:00",
            "2026-06-02 14:50:00",
            "2026-06-02 15:10:00",
            "2026-06-02 15:30:00",
            None
        )
    ]
    schema = [
        "order_id",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
    df_input = spark_fixture.createDataFrame(input_data, schema)

    # 2. Quando (When): Executamos a nossa função de transformação
    df_output = transform_orders(df_input)

    # 3. Então (Then): Validamos se o resultado é o esperado
    result = df_output.collect()

    # Verifica se os tipos viraram Timestamps (não são mais strings)
    assert df_output.schema["order_purchase_timestamp"].dataType.simpleString() == "timestamp"
    # Verifica se a coluna de auditoria 'ingestion_at' foi criada
    assert "ingestion_at" in df_output.columns
    # Verifica se o valor nulo foi preservado corretamente
    assert result[1]["order_approved_at"] is None
