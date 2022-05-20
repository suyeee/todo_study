from pyspark.sql import SparkSession

MAX_MEMORY = "5g"
spark = SparkSession.builder.appName("taxi-fare-prediction")\
    .config("spark.executor.memory", MAX_MEMORY)\
    .config("spark.driver.memory", MAX_MEMORY)\
    .getOrCreate()

# Spark 프로젝트는 주피터 노트북으로 전부 실행 해보고 .py로 만들어서 spark-submit 하면된다.

# Data Loading
trip_files = "/home/lab26/SparkCourse/data/trips/*"
trips_df = spark.read.csv(f"file:///{trip_files}", inferSchema=True, header=True)

# Table Regist
trips_df.createOrReplaceTempView("trips")

# Query 작성
query = """
SELECT
    passenger_count,
    PULocationID as pickup_location_id,
    DOLocationID as dropoff_location_id,
    trip_distance,
    HOUR(tpep_pickup_datetime) as pickup_time,
    DATE_FORMAT(TO_DATE(tpep_pickup_datetime), 'EEEE') AS day_of_week,
    total_amount
FROM
    trips
WHERE
    total_amount < 5000
    AND total_amount > 0
    AND trip_distance > 0
    AND trip_distance < 500
    AND passenger_count < 4
    AND TO_DATE(tpep_pickup_datetime) >= '2021-01-01'
    AND TO_DATE(tpep_pickup_datetime) < '2021-08-01'
"""

# Data warehouse 만들기 (웨어하우스 이면서 동시에 마트..)
dw = spark.sql(query) # 그림으로 설명했던거중 feature store에 해당하는 부분

# 추가
# 데이터 웨어하우스만 구축해도 충분한 경우 - 보통 딥러닝 할때
# 데이터 마트를 구축해야하는 경우 - 일반적인 머신러닝(딥러닝) 및 데이터 분석, 시각화

# 머신러닝을 위한 처리(원래는 사이언스가 하는 일인데 엔지니어링도 할수는 있음.)
train_df, test_df = dw.randomSplit([0.8, 0.2], seed=42)

# train, test 데이터 세트 저장
# 왜 저장을 하지? 매번 다시 실행할때마다 웨어하우스를 만들면 시간이 오래걸리니까 시간을 줄이려고
data_dir = "/home/lab26/airflow/data"

# train_df와 test_df를 기록 한다.
train_df.write.format("parquet").mode("overwrite").save(f"{data_dir}/train/")
test_df.write.format("parquet").mode("overwrite").save(f"{data_dir}/test/")
