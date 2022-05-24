from kafka import KafkaConsumer

# docker에서 사용한 포트 번호들 입력
# Broker 목록은 모두 설정하는것이 좋다.
# AWS 로 쓰는 경우 개인포트번호로 입력
BROKERS = ["localhost:8978", "localhost:8979", "localhost:8980"]

# local에서 작업하는경우 (M1 맥북)
# BROKERS = ["localhost:9091", "localhost:9092", "localhost:9093"]

TOPIC_NAME = "first-lab26-cluster-topic"

consumer = KafkaConsumer(TOPIC_NAME, bootstrap_servers=BROKERS)

print("Wait...")

for message in consumer:
    print(message)

print("Done...")
