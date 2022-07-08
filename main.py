import sys
import os

import boto3
import botocore

s3_session = boto3.session.Session(
    aws_access_key_id=os.getenv("STORAGE_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("STORAGE_SECRET_KEY"),
    region_name=os.getenv("STORGE_REGION"),
)

s3 = s3_session.client(
    service_name="s3",
    endpoint_url=os.getenv("STORAGE_ENDPOINT_URL"),
)

BUCKET = os.getenv("STORAGE_BUCKET")
KEY = "unemployment.csv"


def _query(country):
    res = s3.select_object_content(
        Bucket=BUCKET,
        Key=KEY,
        Expression=f"select * from s3object s where s.country = '{country}'",
        ExpressionType="SQL",
        InputSerialization={
            "CSV": {
                "FileHeaderInfo": "USE",
            },
            "CompressionType": "NONE",
        },
        OutputSerialization={"CSV": {}},
    )

    for row in res["Payload"]:
        if "Records" in row:
            records = row["Records"]["Payload"].decode("utf-8")
            print(records)


def _prepare_data():
    try:
        s3.head_object(Bucket=BUCKET, Key=KEY)
    except botocore.exceptions.ClientError:
        s3.upload_file("data/unemployment_country_age.csv", BUCKET, KEY)


def main(country):
    """Main entry point."""
    _prepare_data()
    _query(country)


if __name__ == "__main__":
    main(country=sys.argv[1])
