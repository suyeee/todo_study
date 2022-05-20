from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALSModel
from pyspark.sql.types import IntegerType

MAX_MEMORY = "5g"

spark = SparkSession.builder.appName("movie-recommendation")\
    .config("spark.executor.memory", MAX_MEMORY)\
    .config("spark.driver.memory", MAX_MEMORY)\
    .getOrCreate()

# 테스트 데이터 불러오기
data_dir = "/home/tutor/airflow/movie_data"
test_df  = spark.read.parquet(f"{data_dir}/test/")

# 모델 불러오기
model = ALSModel.load("/home/lab26/airflow/movie_data/model")

test_user_ids = test_df.select("userId")

# 영화이름 확인
directory = "/home/lab26/SparkCourse/data/ml-25m"
movies_files = "movies.csv"
movies_df = spark.read.csv(f"file:///{directory}/{movies_files}", inferSchema=True, header=True)

def get_recommendations(num_recs=5):
    
    # 각 user에 대해 top 5 추천
    user_recs_df = model.recommendForUserSubset(test_user_ids, num_recs)
    
    recs_list = user_recs_df.collect()[0].recommendations
    recs_df   = spark.createDataFrame(recs_list)
    
    # DataFrame의 join 함수 사용하기
    recommended_movies = recs_df.join(movies_df, "movieId")
    
    return recommended_movies

# csv로 저장
recs = get_recommendations()
recs.to_csv("movie-recommendation.csv")
