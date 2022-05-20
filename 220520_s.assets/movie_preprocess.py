from pyspark.sql import SparkSession

MAX_MEMORY = "5g"

spark = SparkSession.builder.appName("movie-recommendation")\
    .config("spark.executor.memory", MAX_MEMORY)\
    .config("spark.driver.memory", MAX_MEMORY)\
    .getOrCreate()

# 데이터 불러오기
directory = "/home/lab26/SparkCourse/data/ml-25m"
ratings_file = "ratings.csv"
ratings_df = spark.read.csv(f"file:///{directory}/{ratings_file}", inferSchema=True, header=True)

# `timestamp`는 빼고 선택
ratings_df = ratings_df.select(["userId", "movieId", "rating"])

# 훈련, 테스트 세트 분리하기
train_df, test_df = ratings_df.randomSplit([0.8, 0.2], seed=42)

# 데이터 저장
data_dir = "/home/lab26/airflow/movie_data"

# train_df와 test_df를 기록 한다.
train_df.write.format("parquet").mode("overwrite").save(f"{data_dir}/train/")
test_df.write.format("parquet").mode("overwrite").save(f"{data_dir}/test/")