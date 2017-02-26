import threading
from time import sleep

from pykafka import BalancedConsumer
from pykafka import KafkaClient
from pykafka import Producer


class MsgQueue:
    def __init__(self, cluster_addr, topic, consumer_group=None):
        self.consumer_group = consumer_group
        self.topic = topic
        self.cluster_addr = cluster_addr
        print(cluster_addr)
        self.client = KafkaClient(hosts=self.cluster_addr)
        self.topic = self.client.topics[topic.encode()]
        self.consumer_group = consumer_group

        self.consumer = None
        self.producer = None

    def consume(self):
        if not self.consumer:
            if self.consumer_group:
                self.consumer = self.topic.get_simple_consumer(self.consumer_group.encode())
                # self.consumer = self.topic.get_balanced_consumer(self.consumer_group.encode())
            else:
                self.consumer = self.topic.get_simple_consumer()

        return self.consumer

    def commit_offset(self):
        if self.consumer:
            self.consumer.commit_offsets()

    def produce(self, msg):
        if not self.producer:
            self.producer = self.topic.get_producer()

        self.producer.produce(msg)


if __name__ == "__main__":
    msg = MsgQueue("127.0.0.1:9092", "test", "test_group")


    def p():
        while True:
            print(msg.produce(b"hahahah"))
            sleep(10)


    def c():
        for message in msg.consumer:
            if message is not None:
                print(message.offset, message.value)
                pass
            print(msg.commit_offset())


    threading.Thread(target=p).start()
    sleep(1)
    threading.Thread(target=c).start()
