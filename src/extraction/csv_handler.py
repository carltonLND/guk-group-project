import pandas as pd

COLUMN_NAMES = [
    "date_time",
    "branch_name",
    "customer_name",
    "products",
    "total_price",
    "payment_method",
    "card_number",
]


def extract_data(filename):
    file = pd.read_csv(filename, header=None)
    df = pd.DataFrame(file)
    df.index = range(1, len(df) + 1)
    return df


def create_columns(data, column_names):
    data.columns = column_names
    return data
