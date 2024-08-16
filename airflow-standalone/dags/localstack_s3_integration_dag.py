from datetime import datetime, timedelta

import boto3
from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.s3 import S3DeleteObjectsOperator, S3CreateBucketOperator


@dag(
    dag_id="localstack_s3_integration_dag",
    start_date=datetime.today(),
    schedule=timedelta(days=1)
)
def localstack_s3_integration_dag():
    create_bucket = S3CreateBucketOperator(
        task_id="create_bucket",
        bucket_name="python-tutorial-bucket",
        region_name="us-west-2",
        aws_conn_id="localstack_conn"
    )

    def upload_file_to_s3():
        s3 = boto3.client('s3',
                          region_name='us-west-2',
                          endpoint_url='http://localstack:4566',
                          aws_access_key_id='test',
                          aws_secret_access_key='test'
                          )
        s3.upload_file('/opt/airflow/resources/s3-test-file.txt', 'python-tutorial-bucket', 's3-test-file.txt')

    upload_file = PythonOperator(
        task_id="upload_file",
        python_callable=upload_file_to_s3
    )

    delete_files = S3DeleteObjectsOperator(
        task_id="delete_files",
        bucket="python-tutorial-bucket",
        keys="s3-test-file.txt",
        aws_conn_id="localstack_conn"
    )

    (create_bucket >> upload_file >> delete_files)


dag = localstack_s3_integration_dag()
