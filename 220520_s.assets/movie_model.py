from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS

MAX_MEMORY = "5g"

spark = SparkSession.builder.appName("movie-recommendation")\
    .config("spark.executor.memory", MAX_MEMORY)\
    .config("spark.driver.memory", MAX_MEMORY)\
    .getOrCreate()

# 훈련, 테스트 세트 불러오기
data_dir = "/home/lab26/airflow/movie_data"
train_df = spark.read.parquet(f"{data_dir}/train/")
test_df = spark.read.parquet(f"{data_dir}/test/")

als = ALS(
    maxIter=5, # 훈련 반복 횟수
    regParam=0.1,
    
    userCol="userId",
    itemCol="movieId",
    ratingCol="rating",
    
    coldStartStrategy="drop" # 학습하지 못한 데이터에 대한 처리
)

als_model = als.fit(train_df)

# 모델 저장
model_dir = "/home/lab26/airflow/movie_data/model"
als_model.write().overwrite().save(model_dir)
