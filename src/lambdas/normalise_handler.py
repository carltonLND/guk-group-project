import json
import os

import boto3

from src.extraction.csv_handler import COLUMN_NAMES, create_columns, extract_data
from src.normalise.clean import (
    SENSITIVE_COLUMNS,
    format_date_time,
    get_clean_products_df,
    get_product_df,
    get_transaction_df,
    remove_user_info,
)

SOURCE = "delon8-group3"
TARGET = "group3-stack-target-needed"
QUEUE = "group3-normalise-sqs-needed.fifo"

SQS = boto3.client(
    service_name="sqs", endpoint_url="https://sqs.eu-west-1.amazonaws.com"
)
S3 = boto3.client(service_name="s3", endpoint_url="https://s3.eu-west-1.amazonaws.com")


def handler(event, _):
    raw_object_key = event["Records"][0]["s3"]["object"]["key"]
    filename = os.path.basename(raw_object_key)
    path = f"/tmp/{filename}"
    S3.download_file(SOURCE, raw_object_key, path)

    dataframe = remove_user_info(
        create_columns(extract_data(path), COLUMN_NAMES), SENSITIVE_COLUMNS
    )

    transaction_dataframe = format_date_time(get_transaction_df(dataframe))
    product_dataframe = get_clean_products_df(get_product_df(dataframe))

    transaction_object_key = f"transaction_{filename}"
    transaction_path = f"/tmp/{transaction_object_key}"
    transaction_dataframe.to_csv(transaction_path, header=False)
    S3.upload_file(transaction_path, TARGET, transaction_object_key)

    product_object_key = f"product_{filename}"
    product_path = f"/tmp/{product_object_key}"
    product_dataframe.to_csv(product_path, header=False)
    S3.upload_file(product_path, TARGET, product_object_key)

    queue_url = SQS.get_queue_url(QueueName=QUEUE)["QueueUrl"]
    message = json.dumps(
        {
            "bucket": TARGET,
            "files": [transaction_object_key, product_object_key],
        }
    )
    SQS.send_message(
        QueueUrl=queue_url,
        MessageBody=message,
        MessageGroupId=filename,
        MessageDeduplicationId=filename,
    )
