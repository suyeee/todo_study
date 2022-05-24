# payment_producer 한테서 데이터를 Consume
# 정상데이터 -> legit_processor로 프로듀싱
# 이상데이터 -> fraud_processor로 프로듀싱

from kafka import KafkaConsumer, KafkaProducer
import json

PAYMENT_TOPIC = "payments"
FRAUD_TOPIC = "fraud_payments"
LEGIT_TOPIC = "legit_payments"

BROKERS = ["localhost:8978", "localhost:8979", "localhost:8980"]

consumer = KafkaConsumer(PAYMENT_TOPIC, bootstrap_servers=BROKERS)
producer = KafkaProducer(bootstrap_servers=BROKERS)

# 이상한 결제 데이터의 기준을 정의
def is_suspicious(message):
    # stranger가 결제를 했거나, 비트코인으로 결제를 했다면 의심스러운 사람으로 정의
    if message["TO"] == "stranger" or message["PAYMENT_TYPE"] == "비트코인":
        return True
    else:
        return False

for message in consumer:
    msg = json.loads(message.value.decode())

    if is_suspicious(msg):
        producer.send(FRAUD_TOPIC, json.dumps(msg).encode("utf-8"))
    else:
        producer.send(LEGIT_TOPIC, json.dumps(msg).encode("utf-8"))

    print(is_suspicious(msg), msg["PAYMENT_TYPE"], msg["TO"])

