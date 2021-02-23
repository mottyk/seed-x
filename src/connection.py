import logging

import pika

HOST = "rabbitmq"

class RabbitConnection:
    def __init__(self, name):
        self.channel = None
        self.name = name
        self.connection = None

    def get_channel(self):
        if not self.channel:
            self.connection = get_connection()
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.name)
        return self.channel

    def reset_channel(self):
        try:
            if self.connection:
                self.connection.close()
        except Exception as e:
            logging.error(e, exc_info=True)
        self.connection = None
        self.channel = None

    def consume(self, on_callback):
        try:
            self.get_channel().basic_consume(
            queue=self.name,
            on_message_callback=on_callback,
            auto_ack=True)
            logging.info("channel started {}".format(self.name))
            self.channel.start_consuming()
        except Exception as e:
            logging.error(e, exc_info=True)
            exit()


def get_connection():
    credentials = pika.PlainCredentials('user', 'password')
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=HOST, port=5672,
                                                             virtual_host="/",
                                                             credentials=credentials, connection_attempts=5, retry_delay=10,
                                                             heartbeat=None,
                                                             stack_timeout=10,
                                                             socket_timeout=10, blocked_connection_timeout=10))
    return conn