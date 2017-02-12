from pykafka import KafkaClient


def produce():
    client = KafkaClient(hosts="127.0.0.1:9092")
    print(client.topics)
    topic_name =b"test"
    topic = client.topics[topic_name]
    producer  = topic.get_producer()

    msg_list = [("i send message "+str(i)).encode() for i in range(5)]
    print(msg_list)
    producer.produce(b"xxsxsxs now is")

def consume():
    client = KafkaClient(hosts="127.0.0.1:9092")
    topic = client.topics[topic_name]
    consumer = topic

if __name__ == "__main__":
    produce()
