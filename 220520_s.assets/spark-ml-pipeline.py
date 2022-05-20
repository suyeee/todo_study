# airflow
from datetime import datetime 
from airflow import DAG

from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

default_args={
    "start_date": datetime(2022, 1, 1)
}

with DAG(
    dag_id="spark-ml-pipeline",
    schedule_interval="@daily",
    default_args=default_args,
    tags=["spark",'ml','taxi'],
    catchup=False) as dag:

    submit_preprocess = SparkSubmitOperator(
        application="/home/lab26/airflow/dags/preprocess.py",  # spark-submit 할 스파크 어플리케이션 경로
        task_id="submit_preprocess",
        conn_id="spark_local"
    )

    submit_tune_hyperparameter = SparkSubmitOperator(
        application="/home/lab26/airflow/dags/tune_hyperparameter.py", 
        task_id="submit_tune_hyperparameter",
        conn_id="spark_local"
    )

    submit_train_model = SparkSubmitOperator(
        application="/home/lab26/airflow/dags/train_model.py", 
        task_id="submit_train_model",
        conn_id="spark_local"
    )

    submit_preprocess >> submit_tune_hyperparameter >> submit_train_model
    