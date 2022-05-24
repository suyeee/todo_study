from kafka import KafkaConsumer

BROKER_SERVER = ["localhost:9026"]
TOPIC_NAME = "first_lab26_topic"

consumer = KafkaConsumer(TOPIC_NAME, bootstrap_servers=BROKER_SERVER)

# consumer는 파이썬의 Generator로 구성되어있다.
print("Wait....")

for message in consumer:
    print(message)

print("Done....")
