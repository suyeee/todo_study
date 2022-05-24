from kafka import KafkaConsumer
import json

FRAUD_TOPIC = "fraud_payments"
BROKERS = ["localhost:8978", "localhost:8979", "localhost:8980"]

consumer = KafkaConsumer(FRAUD_TOPIC, bootstrap_servers=BROKERS)

for message in consumer:
    msg = json.loads(message.value.decode())
    payment_type = msg["PAYMENT_TYPE"]
    payment_date = msg["DATE"]
    payment_time = msg["TIME"]
    amount = msg["AMOUNT"]
    to = msg["TO"]
    print(f"이상거래 - [{payment_type}] {payment_date} {payment_time} << {to} - {amount} >>")