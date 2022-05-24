from kafka import KafkaProducer
import datetime
import pytz  # 패키지 없으면 'pip install pytz' 로 설치
import time
import random
import json

# 토픽이름부터 정의
TOPIC_NAME = "payments"
BROKERS = ["localhost:8978", "localhost:8979", "localhost:8980"]

# Producer 생성
producer = KafkaProducer(bootstrap_servers=BROKERS)

# 현재시간을 Asia/Seoul timezone에 맞춰서 생성
def get_seoul_date():
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    kst_now = utc_now.astimezone(pytz.timezone("Asia/Seoul"))
    d = kst_now.strftime("%m/%d/%Y")
    t = kst_now.strftime("%H:%M:%S")
    return d, t

# 결제정보 데이터 생성기. 랜덤하게 결제 정보를 만들어준다.
def generate_payment_data():
    # 데이터 소스로부터 데이터를 끌어오는 기능을 만들어주면 된다.
    # 크롤러나 다른 데이터 레이크에서 데이터를 가져오면 됨.
    payment_type = random.choice(['롯데', '하나', '삼성', '현대', '비트코인'])
    amount = random.randint(1000, 1000000)

    to = random.choice(["me", "mom", "dad", "stranger"])

    return payment_type, amount, to

# 데이터 발생 및 스트리밍
while True:
    d, t = get_seoul_date()
    payment_type, amount, to = generate_payment_data()

    # 스트리밍할 데이터 조립(json으로)
    new_data = {
        "DATE": d,
        "TIME": t,
        "PAYMENT_TYPE": payment_type,
        "AMOUNT": amount,
        "TO": to
    }

    # 프로듀싱
    producer.send(TOPIC_NAME, json.dumps(new_data).encode("utf-8"))
    print(new_data)
    time.sleep(1)
    
