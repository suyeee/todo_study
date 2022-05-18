from datetime import datetime
import json
from airflow import DAG

# pip install pandas 또는 pip3 install pandas 또는 conda install pandas
# 로 터미널에서 설치해준다.
from pandas import json_normalize  # json to pandas (json데이터를 pandas 데이터로 변환)

# Operator Import

# DB Operator - DB 관련 Operator
from airflow.providers.sqlite.operators.sqlite import SqliteOperator

# HTTP Sensor Operator - 웹 사이트에 HTTP 통신을 활용해 접근할수있는지 감지
from airflow.providers.http.sensors.http import HttpSensor

# HTTP - 실제 요청 후 응답을 받아낼수있는 Operator (데이터 획득, 추출이 가능하다!)
from airflow.providers.http.operators.http import SimpleHttpOperator

# Python Operator - Python 코드를 실행하기위한 Operator. 함수나 클래스 등을 직접 실행한다.
from airflow.operators.python import PythonOperator

# bash commandline 을 입력할 수 있게 해준다.
from airflow.operators.bash import BashOperator

# 시작시간 반드시 필요
default_args = {
    "start_date" : datetime(2022, 1, 1) # 2022년 1월 1일 부터 시작.
}

KAKAO_API_KEY = "https://developers.kakao.com/ 에서 REST API 키 확인"

def _preprocessing(ti):
    # ti : task instance
    # dag 내의 task 의 정보를 얻어 낼수있는 객체
    search_result = ti.xcom_pull(task_ids=["extract_kakao"])

    # xcom을 이용해 가지고 온 결과가 아무것도 없다면 어떻게 처리할건지 작성
    if not len(search_result):
        raise ValueError("검색결과가 없습니다.")

    documents = search_result[0]["documents"]
    processed_documents = json_normalize([
    {"created_at": document['datetime'],
     "contents": document['contents'],
     "title": document["title"],
     "url": document["url"]} for document in documents
    ])

    processed_documents.to_csv("/home/lab26/airflow/dags/tmp/processed_result.csv", index=None, header=False)

# DAG 환경을 구성하기위한 Task 정의 context 설정
with DAG(
    dag_id="kakao-pipeline",  # 필수옵션, dag_id -> 구분자
    schedule_interval="@daily",  # crontab 표현으로 사용가능 https://crontab.guru/
    default_args=default_args,
    tags=['kakao', 'api', 'pipeline'],
    catchup=False  # catchup=False 오늘꺼만 실행하고 과거의 작업은 실행하지않는다.
    ) as dag:

    # Operator 만들기
    creating_table = SqliteOperator(
        task_id="creating_table",
        sqlite_conn_id="db_sqlite",  # UI 상에서 connection 등록
        
        # 쿼리 작성 - 테이블 만들기 (IF NOT EXISTS 넣어서 카카오 테이블이 없을때만 만들도록 설정)
        sql='''
            CREATE TABLE IF NOT EXISTS kakao_search_result(
                created_at TEXT,
                contents TEXT,
                title TEXT,
                url TEXT
            )
        '''
    )

    # HTTP 센서를 이용해서 해당 api가 존재하는지 확인
    is_api_available = HttpSensor(
        task_id="is_api_available",
        http_conn_id='kakao_api',
        endpoint="v2/search/web",  # url 설정을 하는 옵션
        headers={"Authorization": f'KakaoAK {KAKAO_API_KEY}'},  # 요청 헤더
        request_params={"query": "아메리카노"},  # 요청 파라미터
        response_check=lambda response: response.json()  # 응답 확인
    )

    extract_kakao = SimpleHttpOperator(
        task_id="extract_kakao",
        http_conn_id='kakao_api',
        endpoint="v2/search/web",  # url 설정을 하는 옵션
        headers={"Authorization": f'KakaoAK {KAKAO_API_KEY}'},  # 요청 헤더
        data={"query": "아메리카노"},  # 요청 파라미터
        method="GET",  # 통신방식 설정. GET, POST 등등 설정 가능
        response_filter=lambda res: json.loads(res.text),
        log_response=True  # 응답 기록들 볼껀지 선택하는 옵션
    )

    # xcom( cross communication) 설정
    # Operator와 Operator 사이에 데이터를 전달할수있게끔 하는 도구

    preprocess_result = PythonOperator(
        task_id="preprocess_result",
        python_callable=_preprocessing  # 실행시킬 함수가 들어간다.
    )

    # csv를 분해 후 table에 넣어주기
    store_result = BashOperator(
        task_id="store_kakao",
        bash_command='echo -e ".separator ","\n.import /home/lab26/airflow/dags/tmp/processed_result.csv kakao_search_result" | sqlite3 /home/lab26/airflow/airflow.db'
    )

    # 파이프라인 구성하기
    creating_table >> is_api_available >> extract_kakao >> preprocess_result >> store_result
