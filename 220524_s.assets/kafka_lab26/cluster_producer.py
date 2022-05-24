from kafka import KafkaProducer

BROKERS = ["localhost:8978", "localhost:8979", "localhost:8980"]
TOPIC_NAME = "first-lab26-cluster-topic"

producer = KafkaProducer(
    bootstrap_servers=BROKERS
)

producer.send(TOPIC_NAME, b"Hello Kafka!!!")
producer.flush()
