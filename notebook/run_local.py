import pandas as pd

def read_csv(path):
    df = pd.read_csv(path)
    print(df.info())

    convert_to_timestamp = [
        'order_purchase_timestamp',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]

    for column in convert_to_timestamp:
        df[column] = pd.to_datetime(df[column])

    # create column order_purchase_year
    df['order_purchase_year'] = df['order_purchase_timestamp'].dt.year
    df['order_purchase_month'] = df['order_purchase_timestamp'].dt.month

    print(df.head().to_string())

    print(df['order_purchase_year'].value_counts())

    # meses com mais compra
    print(df.groupby('order_purchase_month').size())

if __name__ == '__main__':
    read_csv('../raw_files/olist_orders_dataset.csv')
