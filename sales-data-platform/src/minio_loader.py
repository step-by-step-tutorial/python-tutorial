import boto3
import pandas as pd


class MinioLoader:
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
    ):
        self.bucket_name = bucket_name
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    def create_bucket_if_not_exists(self) -> None:
        buckets = self.client.list_buckets()["Buckets"]
        existing_bucket_names = [bucket["Name"] for bucket in buckets]

        if self.bucket_name not in existing_bucket_names:
            self.client.create_bucket(Bucket=self.bucket_name)

    def upload_parquet(
        self,
        df: pd.DataFrame,
        local_path: str,
        object_key: str,
    ) -> None:
        self.create_bucket_if_not_exists()

        df.to_parquet(local_path, index=False)

        self.client.upload_file(
            local_path,
            self.bucket_name,
            object_key,
        )