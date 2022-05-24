# CSV 파일을 열어서 한줄 한줄 스트리밍
from kafka import KafkaProducer

import csv
import json
import time

BROKERS = ["localhost:8978", "localhost:8979", "localhost:8980"]
TOPIC_NAME = "first-lab26-cluster-topic"

producer = KafkaProducer(bootstrap_servers=BROKERS)

# csv 파일 열기
with open("./trips/yellow_tripdata_2021-01.csv") as f:
    reader = csv.reader(f)  # csv 를 한줄 한줄 읽게 도와주는 역할

    # reader 에서 한줄씩 읽어오기
    for row in reader:
        time.sleep(0.5)  # 0.5초씩 딜레이 주면서 실행하게끔 (안해도 되는데 더 잘 확인하기위해)
        producer.send(TOPIC_NAME, json.dumps(row).encode("utf-8"))
        print(row)
