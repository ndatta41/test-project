import pika
import json
import logging
import yaml
import os

config_path = os.getenv('CONFIG_PATH', 'config.yaml')
with open(config_path, 'r') as file:
    config = yaml.safe_load(config_path)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.FileHandler('logs/consumer.log'),
              logging.StreamHandler()]
)

RABBITMQ_HOST = config['rabbitmq']['host']
QUEUE_NAME = config['rabbitmq']['queue']

def callback(channel, method, properties, body):
    message = json.loads(body.decode())
    logging.info(f"Received: {json.dumps(message, indent=4)}")
    channel.basic_ack(delivery_tag=method.delivery_tag)

def consume_message():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    logging.info("Waiting for messages. To exit, press CTRL+C")
    channel.stop_consuming()

if __name__ == '__main__':
    consume_message()