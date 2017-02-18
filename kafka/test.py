from pykafka import KafkaClient

from lib.MsgQueue import MsgQueue


def get_topic():
    client = KafkaClient(hosts="127.0.0.1:9092")
    t = client.topics[b"sea_jd_result_queue"]
    c = t.get_simple_consumer()
    m = c.consume()
    print(m.value)
if __name__ == "__main__":
    get_topic()

