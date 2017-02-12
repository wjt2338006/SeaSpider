import threading
from time import sleep

from pykafka import BalancedConsumer
from pykafka import KafkaClient
from pykafka import Producer


class MsgQueue:
    def __init__(self,cluster_addr,topic,consumer_group):
        self.consumer_group = consumer_group
        self.topic = topic
        self.cluster_addr = cluster_addr

        self.client = KafkaClient(hosts="127.0.0.1:9092")
        self.topic = self.client.topics[topic.encode()]
        self.balanced_consumer = self.topic.get_balanced_consumer(consumer_group.encode())
        self.producer = self.topic.get_producer()

    def consume(self):
        self.balanced_consumer.consume()

    def commit_offset(self):
        self.balanced_consumer.commit_offsets()

    def produce(self,msg):
        self.producer.produce(msg)


if __name__ == "__main__":
    msg = MsgQueue("127.0.0.1:9092","test","test_group")


    def p():
        print(msg.produce(b"caonimabi"))
    def c():
        for message in  msg.balanced_consumer:
            if message is not None:
                print(message.offset, message.value)
    threading.Thread(target=p).start()
    sleep(1)
    threading.Thread(target=c).start()