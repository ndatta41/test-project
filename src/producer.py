import time

import pika
import uuid
import json
import logging
from datetime import datetime
import yaml
import os

config_path = os.getenv('CONFIG_PATH', 'config/config.yaml')
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.FileHandler('logs/producer.log'),
              logging.StreamHandler()]
)

RABBITMQ_HOST = config['rabbitmq']['host']
QUEUE_NAME = config['rabbitmq']['queue']
INTERVAL = config['producer']['interval']


def connect_to_rabbitmq(retry_count):
    while retry_count > 0:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST
                )
            )
            return connection
        except pika.exceptions.AMQPConnectionError:
            logging.info("RabbitMQ not available, retrying in 5 seconds...")
            time.sleep(5)
            retry_count = retry_count - 1

def send_message():
    connection = connect_to_rabbitmq(3)
    channel = connection.channel()
    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True
    )

    while True:
        message = {
            'message_id': str(uuid.uuid4()),
            'created_on': datetime.now().isoformat()
        }
        message_json = json.dumps(message)
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=message_json,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        logging.info(f"sent: {message_json}")
        time.sleep(INTERVAL)

    connection.close()

if __name__ == '__main__':
    send_message()