import json

import boto3
import psycopg2

STAGING = "group3-stack-staging-needed"
ROLE = "arn:aws:iam::948243690849:role/RedshiftS3Role"

SSM = boto3.client("ssm")

response = SSM.get_parameter(Name="redshift-group-3", WithDecryption=True)
DB_SECRETS = json.loads(response["Parameter"]["Value"])


def handler(event, context):
    # load csv from event
    message = json.loads(event["Records"][0]["body"])
    bucket = message["bucket"]
    files = message["files"]

    # connect to a database
    connector = psycopg2.connect(**DB_SECRETS)

    # insert into database
    try:
        print("CONNECTION OPENED")
        with connector.cursor() as curs:
            print("COPYING TO TRANSACTIONS")
            curs.execute(
                "COPY staging.transactions FROM %s IAM_ROLE %s CSV;",
                (
                    f"s3://{bucket}/{files[0]}",
                    ROLE,
                ),
            )

        with connector.cursor() as curs:
            print("COPYING TO PRODUCTS")
            curs.execute(
                "COPY staging.products FROM %s IAM_ROLE %s CSV;",
                (
                    f"s3://{bucket}/{files[1]}",
                    ROLE,
                ),
            )

        with connector.cursor() as curs:
            print("UPDATE TRANSACTIONS")
            curs.execute(
                """
                UPDATE staging.transactions
                SET id = id + (
                    SELECT NVL(MAX(id), 0)
                    FROM public.transactions
                );
                """
            )

        with connector.cursor() as curs:
            print("UPDATE PRODUCTS")
            curs.execute(
                """
                UPDATE staging.products
                SET id = id + (
                    SELECT NVL(MAX(id), 0)
                    FROM public.products
                ),
                transaction_id = transaction_id + (
                    SELECT NVL(MAX(transaction_id), 0)
                    FROM public.products
                );
                """
            )

        with connector.cursor() as curs:
            print("UNLOADING TRANSACTIONS")
            curs.execute(
                """
                UNLOAD ( 'SELECT * FROM staging.transactions' )
                TO %s
                IAM_ROLE %s
                REGION 'eu-west-1'
                PARALLEL OFF
                ALLOWOVERWRITE
                CSV;
                """,
                (
                    f"s3://{STAGING}/staging_transactions.csv",
                    ROLE,
                ),
            )

        with connector.cursor() as curs:
            print("UNLOADING PRODUCTS")
            curs.execute(
                """
                UNLOAD ( 'SELECT * FROM staging.products' )
                TO %s
                IAM_ROLE %s
                REGION 'eu-west-1'
                PARALLEL OFF
                ALLOWOVERWRITE
                CSV;
                """,
                (
                    f"s3://{STAGING}/staging_products.csv",
                    ROLE,
                ),
            )

        with connector.cursor() as curs:
            print("COPYING TO TRANSACTIONS")
            curs.execute(
                "COPY public.transactions FROM %s IAM_ROLE %s CSV;",
                (
                    f"s3://{STAGING}/staging_transactions.csv000",
                    ROLE,
                ),
            )

        with connector.cursor() as curs:
            print("COPYING TO PRODUCTS")
            curs.execute(
                "COPY public.products FROM %s IAM_ROLE %s CSV;",
                (
                    f"s3://{STAGING}/staging_products.csv000",
                    ROLE,
                ),
            )

        with connector.cursor() as curs:
            print("DELETING STAGING TRANSACTIONS")
            curs.execute("TRUNCATE TABLE staging.transactions;")

        with connector.cursor() as curs:
            print("DELETING STAGING PRODUCTS")
            curs.execute("TRUNCATE TABLE staging.products;")

        # commit changes and close connection
        connector.commit()
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        print("CONNECTION CLOSED")
        connector.close()
