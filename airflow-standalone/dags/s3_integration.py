from datetime import datetime, timedelta

import boto3
from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.s3 import S3DeleteObjectsOperator, S3CreateBucketOperator


def upload_resource_to_s3(name: str):
    s3 = boto3.client('s3',
                      region_name='us-west-2',
                      endpoint_url='http://localstack:4566',
                      aws_access_key_id='test',
                      aws_secret_access_key='test'
                      )
    s3.upload_file('/opt/airflow/resources/%s' % name, 'python-tutorial-bucket', '%s' % name)


@dag(
    dag_id="s3_integration",
    start_date=datetime.today(),
    schedule=timedelta(days=1)
)
def main_dag():
    bucket_name = "python-tutorial-bucket"
    file_name = "s3-test-file.txt"

    create_bucket = S3CreateBucketOperator(
        task_id="create_bucket",
        bucket_name="%s" % bucket_name,
        region_name="us-west-2",
        aws_conn_id="localstack_conn"
    )

    upload_file = PythonOperator(
        task_id="upload_file",
        python_callable=lambda: upload_resource_to_s3(name=file_name)
    )

    delete_files = S3DeleteObjectsOperator(
        task_id="delete_files",
        bucket=bucket_name,
        keys=[file_name],
        aws_conn_id="localstack_conn"
    )

    create_bucket >> upload_file >> delete_files


dag = main_dag()
