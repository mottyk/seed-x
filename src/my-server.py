#!/usr/bin/env python

# How to send an web socket message using http://www.tornadoweb.org/.
# to get ready you have to install pika and tornado
# 1. pip install pika
# 2. pip install tornado
import asyncio
import json
import logging
from datetime import datetime
from threading import Thread
import tornado.ioloop
import tornado.web
import tornado.websocket
import Classifier
from connection import RabbitConnection

logging.basicConfig(level=logging.INFO)

# web socket clients connected.
clients = []

MESSAGE_QUEUE = "messages"
RESULT_QUEUE = "result"


msg_rabbit_conn = RabbitConnection(MESSAGE_QUEUE)
result_rabbit_conn = RabbitConnection(RESULT_QUEUE)


def messege_callback(ch, method, properties, body):
    for itm in clients:
        msg = json.loads(body)
        ts = list(msg.keys())[0]
        msg = msg[ts]["msg"]

        itm.write_message(body)

        try:
            channel = result_rabbit_conn.get_channel()

            channel.basic_publish(exchange='',
                                               routing_key=RESULT_QUEUE,
                                               body = json.dumps({ts : {"msg": msg, "result": Classifier.classify(msg)}}))
            print("msg in {}".format(json.loads(body)))
        except Exception as e:
            logging.error(e, exc_info=True)
            result_rabbit_conn.reset_channel()

def result_callback(ch, method, properties, body):
    for itm in clients:
        print("result in {}".format(json.loads(body)))
        itm.write_message(body)

def start_consumers(channel):
    asyncio.set_event_loop(asyncio.new_event_loop())
    logging.info("starting channel {}".format(channel))
    connection = RabbitConnection(channel)
    connection.consume(messege_callback if  channel == MESSAGE_QUEUE else result_callback)


class SocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        logging.info('WebSocket opened')
        clients.append(self)

    def on_close(self):
        logging.info('WebSocket closed')
        clients.remove(self)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("websocket.html")


class SendHandler(tornado.web.RequestHandler):
    def get(self):
        content = self.get_arguments("content")[0]
        msg = {str(datetime.now()):{"msg":content}}
        try:
            channel = msg_rabbit_conn.get_channel()
            channel.basic_publish(exchange='',
                                      routing_key=MESSAGE_QUEUE,
                                      body= json.dumps(msg))
            self.write({str(datetime.now()):content})
        except Exception as c:
            logging.error(c, exc_info=True)
            msg_rabbit_conn.reset_channel()


def make_app():
    return tornado.web.Application([
        (r'/ws', SocketHandler),
        (r"/sm", SendHandler),
        (r"/", MainHandler),
    ])


class WebServer(tornado.web.Application):

    def __init__(self):
        handlers = [(r'/ws', SocketHandler),
                    (r"/sm", SendHandler),
                    (r"/", MainHandler), ]
        settings = {'debug': True}
        super().__init__(handlers, **settings)

    def run(self, port=8888):
        self.listen(port)
        tornado.ioloop.IOLoop.instance().start()


ws = WebServer()


def start_server():
    asyncio.set_event_loop(asyncio.new_event_loop())
    ws.run()


if __name__ == "__main__":
    logging.info('Starting thread Tornado')
    threadC = Thread(target=start_consumers, args=("messages",))
    threadC.start()

    threadD = Thread(target=start_consumers, args=("result",))
    threadD.start()

    from threading import Thread

    t = Thread(target=start_server, args=())
    t.daemon = True
    t.start()

    t.join()
    try:
        input("Server ready. Press enter to stop\n")
    except SyntaxError:
        pass
    logging.info('See you...')
