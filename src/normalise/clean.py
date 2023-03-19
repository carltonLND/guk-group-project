import pandas as pd

SENSITIVE_COLUMNS = ["customer_name", "card_number"]


def remove_user_info(data_frame, sensitive_columns):
    return data_frame.drop(columns=sensitive_columns)


def get_product_size(unique_products_list):
    product_sizes = []
    for row in unique_products_list:
        product_size = row.split(" ")[0]
        product_sizes.append(product_size)

    return {"size": product_sizes}


def get_product_df(dataframe):
    return dataframe.drop(
        columns=["date_time", "branch_name", "total_price", "payment_method"]
    )


def get_transaction_df(dataframe):
    return dataframe.drop(columns="products")


def get_product_name(txt):
    info_list = txt.split(" - ")
    for index, s in enumerate(info_list):
        if _check_float(s):
            info_list.pop(index)
    return " ".join(info_list)


def get_price(txt):
    for s in txt.split(" - "):
        if _check_float(s):
            return float(s)


def to_dict(row_index, unique_product):
    unique_product = {
        "product_name": get_product_name(unique_product),
        "quantity": 0,
        "transaction_id": row_index,
        "price": get_price(unique_product),
    }
    return unique_product


def get_products(row):
    products_in_row = row["products"].split(",")
    for product_index, product in enumerate(products_in_row):
        products_in_row[product_index] = product.strip()
    return products_in_row


def get_unique_products(products):
    unique_products = []
    for product in products:
        if product not in unique_products:
            unique_products.append(product)
    return unique_products


def update_quantity(products):
    unique_products = get_unique_products(products)
    for unique_product in unique_products:
        for product in products:
            if unique_product["product_name"] == product["product_name"]:
                unique_product["quantity"] += 1

    return unique_products


def clean_product_row(row, row_index):
    products = get_products(row)
    products = [to_dict(row_index, product) for product in products]
    products = update_quantity(products)
    return products


def update_index(df):
    df.index = range(1, len(df) + 1)
    return df


def get_clean_products_df(extracted_df):
    cleaned_rows = []
    for row_index, row in extracted_df.iterrows():
        cleaned_products = clean_product_row(row, row_index)
        for product in cleaned_products:
            cleaned_rows.append(product)
    df = pd.DataFrame(cleaned_rows)
    df.index = range(1, len(df) + 1)
    return df


def format_date_time(dataframe):
    dataframe["date_time"] = pd.to_datetime(dataframe["date_time"])
    return dataframe


def _check_float(substring: str) -> bool:
    try:
        float(substring)
        return True
    except ValueError:
        return False
