from kafka import KafkaProducer

# 브로커 생성시에는 브로커의 호스트들의 리스트를 준비한다.
# 한개만 알아도 상관없지만 모든 브로커들의 리스트를 입력하는것을 권장
BROKER_SERVER = ["localhost:9026"]
TOPIC_NAME = "first_lab26_topic"

# 프로듀스 생성
producer = KafkaProducer(bootstrap_servers=BROKER_SERVER)

# 브로커에게 토픽에 맞는 데이터를 전송
producer.send(TOPIC_NAME, b'Hello world Kafka!')

# 버퍼 스트림 제거(안해도 상관없는데 권장함.)
producer.flush()
