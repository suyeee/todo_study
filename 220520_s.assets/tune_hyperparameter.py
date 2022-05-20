from pyspark.sql import SparkSession
from pyspark.ml import Pipeline

# feature 준비
from pyspark.ml.feature import OneHotEncoder, StringIndexer # 범주형 데이터를 다루기 위함
from pyspark.ml.feature import VectorAssembler, StandardScaler # 수치형 데이터를 다루기 위함

# Model
from pyspark.ml.regression import LinearRegression

# Validate, Tuning
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.evaluation import RegressionEvaluator

MAX_MEMORY = "5g"
spark = SparkSession.builder.appName("taxi-fare-prediction")\
    .config("spark.executor.memory", MAX_MEMORY)\
    .config("spark.driver.memory", MAX_MEMORY)\
    .getOrCreate()

# 훈련데이터 가져오기
data_dir = "/home/lab26/airflow/data"
train_df = spark.read.parquet(f"{data_dir}/train/")

# 훈련데이터의 양이 매우 많으므로 쓸 양을 제한해준다(10퍼센트의 데이터만 선택)
# 실무에서는 이렇게 하면 안됨. 수업이니까 이렇게 한거
# 미니 배치: 거대한 데이터 웨어하우스에서 일부의 데이터만 랜덤하게 추출한 결과
toy_df = train_df.sample(False, 0.1, seed=42)  # 일부의 데이터를 랜덤하게 뽑는것

# Spark ML 파이프라인 구성하기

stages = []

# 범주형 데ㅣ터에 대한 파이프라인 구성
# StringIndexer => OneHotEncoder
cat_features = [
    "pickup_location_id",
    "dropoff_location_id",
    "day_of_week"
]

for c in cat_features:
    cat_indexer = StringIndexer(inputCol=c, outputCol=c+"_idx").setHandleInvalid("keep")
    onehot_encoder = OneHotEncoder(inputCols=[cat_indexer.getOutputCol()], outputCols=[c+"_onehot"])
    stages += [cat_indexer, onehot_encoder]

# 수치형 데이터들에 대한 처리
# 각 열을 모아서(VectorAssembler) => 표준화(StandardScaler)
num_features = [
    "passenger_count",
    "trip_distance",
    "pickup_time"
]

for n in num_features:
    num_assembler = VectorAssembler(inputCols=[n], outputCol=n+"_vector")
    num_scaler = StandardScaler(inputCol=num_assembler.getOutputCol(), outputCol=n+"_scaled")
    stages += [num_assembler, num_scaler]

# 훈련데이터(feature vector)를 만들기 위한 실제로 사용할 데이터에 대한 Assemble
assembler_input = [c+"_onehot" for c in cat_features] + [n+"_scaled" for n in num_features]  # 리스트와 리스트를 더해서 확장
assembler = VectorAssembler(inputCols=assembler_input, outputCol="features")
stages += [assembler]

# 모델 생성
lr = LinearRegression(
    maxIter=30,
    solver="normal",
    labelCol="total_amount",
    featuresCol="features"
)

# 모델도 스테이지에 등록
stages += [lr]

# 파이프라인 생성
# 모델을 훈련시키고 최적의 파라미터를 찾는 과정
pipeline = Pipeline(stages=stages)

# 하이퍼 파라미터 튜닝
# 하이퍼 파라미터 : 모델이 학습하는 값이 아닌, 사람이 직접 모델에 넣어주는 값

# ParamGridBuilder : 모델이 사용할 하이퍼 파라미터를 여러개 준비시키는것
param_grid = ParamGridBuilder()\
                .addGrid(lr.elasticNetParam, [0.1, 0.2, 0.3, 0.4, 0.5])\
                .addGrid(lr.regParam, [0.1, 0.2, 0.3, 0.4, 0.5])\
                .build()

cross_val = CrossValidator( estimator=pipeline,
                            estimatorParamMaps=param_grid,
                            evaluator=RegressionEvaluator(labelCol="total_amount"),
                            numFolds=5)

# 모델 훈련
cv_model = cross_val.fit(toy_df) # 실제로는 가지고있는 데이터세트 모두를 넣어줘야됨.

# 훈련이 끝났으면 성능이 제일 좋았던 모델을 가지고온다.
best_model = cv_model.bestModel.stages[-1]

# 성능이 제일 좋았던 하이퍼 파라미터만 뽑아내기

# LinearRegression 파라미터
bestElasticNetParam_alpha = best_model._java_obj.getElasticNetParam()
bestRegParam = best_model._java_obj.getRegParam()

hyperparams = {
    "alpha" : [bestElasticNetParam_alpha],
    'reg_param' : [bestRegParam]
}

import pandas as pd
hyper_df = pd.DataFrame(hyperparams).to_csv(f"{data_dir}/hyperparameter.csv")