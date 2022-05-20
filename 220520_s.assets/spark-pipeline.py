from datetime import datetime
from airflow import DAG 

# SparkSql을 airflow 상에서 실행하기 위한 Operator
# 기본적으로 스파크는 무거운 작업을 하기때문에 airflow 에서 돌리면 부담... SparkSubmitOperator
from airflow.providers.apache.spark.operators.spark_sql import SparkSqlOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

default_args={
    "start_date": datetime(2022, 1, 1)
}

with DAG(
    dag_id="spark-pipeline",
    schedule_interval="@daily",
    default_args=default_args,
    tags=["spark"],
    catchup=False) as dag:

    # 간단하고 가벼운 쿼리는 airflow에서 수행해도 좋으나 무거운 쿼리는 spark-submit을 활용하자 
    # sql_job = SparkSqlOperator(
    #     sql="""
    #         select *
    #         from my_table
    #     """,
    #     master="local",
    #     # master = "spark://spark-master-host:port"
    #     task_id="sql_job"
    # )

    # 기본적으로 무거운 spark의 작업을 airflow에서 사용하려면 SparkSubmitOperator를 사용하자~!
    submit_job = SparkSubmitOperator(
        application="/home/lab26/airflow/dags/count_trips.py",  # spark-submit 할 스파크 어플리케이션 경로
        task_id="submit_job",
        conn_id="spark_local"
    )