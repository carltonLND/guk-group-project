from unittest.mock import patch

import pandas as pd
import pytest

from src.normalise import clean
from src.normalise.clean import (
    SENSITIVE_COLUMNS,
    clean_product_row,
    get_price,
    get_product_size,
    get_products,
    get_unique_products,
    remove_user_info,
    to_dict,
    update_quantity,
)


@pytest.fixture
def sensitive_data():
    data = {
        "id": [1, 2],
        "customer_name": ["Nayan", "Sharjeel"],
        "branch_name": ["Chesterfield", "London"],
        "card_number": [5494173772652516, 1166596230622281],
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_product_size():
    return ["Large Cake", "Small Sausage", "Regular Coffee"]


@pytest.fixture
def mock_product_row():
    file = pd.read_csv(
        "tests/mock_data/mock.csv",
        header=None,
    )
    df = pd.DataFrame(file)
    df.columns = [
        "date_time",
        "branch_name",
        "customer_name",
        "products",
        "total_price",
        "payment_method",
        "card_number",
    ]

    df.drop(columns=["date_time", "branch_name", "total_price", "payment_method"])
    for _, row in df.iterrows():
        return row


def test_dropped_columns(sensitive_data):

    result = remove_user_info(sensitive_data, SENSITIVE_COLUMNS)

    for column in SENSITIVE_COLUMNS:
        assert column not in result.columns


def test_product_size_column(mock_product_size):
    expected = {"size": ["Large", "Small", "Regular"]}
    result = get_product_size(mock_product_size)
    assert result == expected


def test_get_products_in_row(mock_product_row):
    actual = get_products(mock_product_row)
    expected = [
        "Regular Flavoured iced latte - Vanilla - 2.75",
        "Regular Flavoured latte - Hazelnut - 2.55",
        "Large Flat white - 2.45",
    ]
    assert actual == expected


def test_get_price():
    mock_product = "Large Flavoured iced latte - Caramel - 3.25"
    actual = get_price(mock_product)
    expected = 3.25
    assert actual == expected


@patch("src.normalise.clean.get_product_name")
@patch("src.normalise.clean.get_price")
def test_to_dict(mock_price, mock_name):
    mock_row_index = 1
    mock_name.return_value = "Large Flavoured iced latte Caramel"
    mock_price.return_value = 3.25
    clean.get_price
    mock_product = "Large Flavoured iced latte - Caramel - 3.25"
    actual = to_dict(mock_row_index, mock_product)
    expected = {
        "product_name": "Large Flavoured iced latte Caramel",
        "quantity": 0,
        "transaction_id": 1,
        "price": 3.25,
    }
    assert actual == expected


def test_update_quantity():
    mock_products = [
        {
            "product_name": "Large Flavoured iced latte Caramel",
            "quantity": 0,
            "transaction_id": 1,
            "price": 0,
        },
        {
            "product_name": "Large Flavoured iced latte Caramel",
            "quantity": 0,
            "transaction_id": 1,
            "price": 0,
        },
        {
            "product_name": "Regular Flavoured iced latte Hazelnut",
            "quantity": 0,
            "transaction_id": 1,
            "price": 0,
        },
    ]

    actual = update_quantity(mock_products)
    expected = [
        {
            "product_name": "Large Flavoured iced latte Caramel",
            "quantity": 2,
            "transaction_id": 1,
            "price": 0,
        },
        {
            "product_name": "Regular Flavoured iced latte Hazelnut",
            "quantity": 1,
            "transaction_id": 1,
            "price": 0,
        },
    ]

    assert actual == expected


def test_get_unique_products():
    mock_products = [
        {
            "product_name": "Large Flavoured iced latte Caramel",
            "quantity": 0,
            "transaction_id": 1,
            "price": 0,
        },
        {
            "product_name": "Large Flavoured iced latte Caramel",
            "quantity": 0,
            "transaction_id": 1,
            "price": 0,
        },
        {
            "product_name": "Regular Flavoured iced latte Hazelnut",
            "quantity": 0,
            "transaction_id": 1,
            "price": 0,
        },
    ]

    actual = get_unique_products(mock_products)
    expected = [
        {
            "product_name": "Large Flavoured iced latte Caramel",
            "quantity": 0,
            "transaction_id": 1,
            "price": 0,
        },
        {
            "product_name": "Regular Flavoured iced latte Hazelnut",
            "quantity": 0,
            "transaction_id": 1,
            "price": 0,
        },
    ]

    assert actual == expected


@patch("src.normalise.clean.get_products")
@patch("src.normalise.clean.to_dict")
@patch("src.normalise.clean.update_quantity")
def test_clean_product_row(
    mock_update_quantity, mock_to_dict, mock_get_products, mock_product_row
):
    mock_get_products.return_value = [
        "Large Flavoured iced latte - Caramel - 3.25",
        "Large Flavoured iced latte - Caramel - 3.25",
        "Regular Flavoured iced latte - Hazelnut - 2.75",
    ]
    mock_to_dict.return_value = [
        {
            "product_name": "Large Flavoured iced latte Caramel",
            "quantity": 0,
            "transaction_id": 1,
            "price": 0,
        },
        {
            "product_name": "Large Flavoured iced latte Caramel",
            "quantity": 0,
            "transaction_id": 1,
            "price": 0,
        },
        {
            "product_name": "Regular Flavoured iced latte Hazelnut",
            "quantity": 0,
            "transaction_id": 1,
            "price": 0,
        },
    ]

    mock_update_quantity.return_value = [
        {
            "product_name": "Large Flavoured iced latte Caramel",
            "quantity": 2,
            "transaction_id": 1,
            "price": 0,
        },
        {
            "product_name": "Regular Flavoured iced latte Hazelnut",
            "quantity": 1,
            "transaction_id": 1,
            "price": 0,
        },
    ]

    actual = clean_product_row(mock_product_row, 1)
    expected = [
        {
            "product_name": "Large Flavoured iced latte Caramel",
            "quantity": 2,
            "transaction_id": 1,
            "price": 0,
        },
        {
            "product_name": "Regular Flavoured iced latte Hazelnut",
            "quantity": 1,
            "transaction_id": 1,
            "price": 0,
        },
    ]

    assert actual == expected
