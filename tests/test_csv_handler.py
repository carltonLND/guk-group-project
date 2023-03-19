import pandas as pd
import pytest

from src.extraction.csv_handler import COLUMN_NAMES, create_columns, extract_data


def test_extract_csv_happy():
    mock_csv_filename = "tests/mock_data/mock.csv"

    extracted_data = extract_data(mock_csv_filename)
    assert len(extracted_data) == 3


def test_extract_csv_sad():
    none_csv_filename = "tests/mock_data/no_file.csv"

    with pytest.raises(FileNotFoundError):
        extract_data(none_csv_filename)


def test_extract_csv_empty():
    empty_csv_file = "tests/mock_data/mock_empty.csv"

    with pytest.raises(pd.errors.EmptyDataError):
        extract_data(empty_csv_file)


def test_column_addition():
    df = pd.read_csv("tests/mock_data/mock.csv", header=None)
    df_w_column = create_columns(df, COLUMN_NAMES)

    assert df_w_column.shape[0] == 3
