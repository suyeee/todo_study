from kafka import KafkaConsumer
import json

BROKERS = ["localhost:8978", "localhost:8979", "localhost:8980"]
TOPIC_NAME = "first-lab26-cluster-topic"

consumer = KafkaConsumer(TOPIC_NAME, bootstrap_servers=BROKERS)

for message in consumer:
    # message에서 value를 추출하면 Producer가 보낸값을 보여줌
    row = json.loads(message.value.decode())

    # 머신러닝 파이프라인을 태우는것도 가능
    #  - 실시간 예측
    #  - 실시간 군집 등...
    # 실시간 데이터 시각화(d3.js, tabelau, PowerBI 등등...)
    
    print(row)
