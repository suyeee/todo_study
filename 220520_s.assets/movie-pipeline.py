from datetime import datetime 
from airflow import DAG

from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

default_args={
    "start_date": datetime(2022, 1, 1)
}

with DAG(
    dag_id="movie-pipeline",
    schedule_interval="@daily",
    default_args=default_args,
    tags=["spark",'ml','movie'],
    catchup=False) as dag:

    movie_preprocess = SparkSubmitOperator(
        application="/home/lab26/airflow/dags/movie_preprocess.py",  # spark-submit 할 스파크 어플리케이션 경로
        task_id="movie_preprocess",
        conn_id="spark_local"
    )

    movie_model = SparkSubmitOperator(
        application="/home/lab26/airflow/dags/movie_model.py", 
        task_id="movie_model",
        conn_id="spark_local"
    )

    movie_recommendation = SparkSubmitOperator(
        application="/home/lab26/airflow/dags/movie_recommendation.py", 
        task_id="movie_recommendation",
        conn_id="spark_local"
    )

    movie_preprocess >> movie_model >> movie_recommendation
    