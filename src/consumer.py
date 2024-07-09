import pika
import json
import logging
import yaml
import os
import time

config_path = os.getenv('CONFIG_PATH', 'config/config.yaml')
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

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

def consume_message():
    connection = connect_to_rabbitmq(3)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    logging.info("Waiting for messages. To exit, press CTRL+C")
    channel.start_consuming()

if __name__ == '__main__':
    consume_message()