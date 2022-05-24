from kafka import KafkaConsumer
import json

LEGIT_TOPIC = "legit_payments"
BROKERS = ["localhost:8978", "localhost:8979", "localhost:8980"]

consumer = KafkaConsumer(LEGIT_TOPIC, bootstrap_servers=BROKERS)

for message in consumer:
    msg = json.loads(message.value.decode())
    payment_type = msg["PAYMENT_TYPE"]
    payment_date = msg["DATE"]
    payment_time = msg["TIME"]
    amount = msg["AMOUNT"]
    to = msg["TO"]
    print(f"[{payment_type}] {payment_date} {payment_time} << {to} - {amount} >>")