#!/usr/bin/env python
# !-*- coding: utf-8 -*-

import json
import time
import redis
import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornadoredis
from logger.logger import logger


# GET settings
SERVER = '127.0.0.1'
PORT = 7777


redis_client = redis.Redis()


class TornadoRedisClient(object):

    def __init__(self):
        self.websockets = []
        self._redis_client = tornadoredis.Client()
        self._redis_client.connect()

    @tornado.gen.coroutine
    def subscribe_redis_channel(self, channel):
        # subscribe to channel
        yield tornado.gen.Task(self._redis_client.subscribe, channel)
        self._redis_client.listen(self.on_redis_message)

    def on_redis_message(self, msg):
        if msg.kind == 'message':
            msg_body_obj = json.loads(str(msg.body))
            msg_body_obj['server_time'] = time.time()
            self.send_message_to_websockets(json.dumps(msg_body_obj))

    def send_message_to_websockets(self, msg):
        for ws in self.websockets:
            ws.send_message(msg)

    def add_websocket(self, websocket):
        self.websockets.append(websocket)

    def remove_websocket(self, websocket):
        self.websockets.remove(websocket)


tornado_redis_client = TornadoRedisClient()
tornado_redis_client.subscribe_redis_channel('publish_channel')


class PublicInfo(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self, token):
        # find user by his token in redis
        self._token = token
        self._profile_hash = redis_client.get(self._token).decode("utf-8")

        if not self._profile_hash:
            # logger.debug("can't find token %s in redis" % self._token)
            # Посылаем клиенту сообщение, что доступ закрыт клиенту
            self.write_message("Access denied")
            self.close()
            return

        logger.debug("WebSocket PublicInfo on_open")
        tornado_redis_client.add_websocket(self)

    def send_message(self, message):
        self.write_message(message)

    def on_close(self):
        tornado_redis_client.remove_websocket(self)
        logger.debug("WebSocket PublicInfo on_close")


class PrivateInfo(tornado.websocket.WebSocketHandler):
    _profile_hash = None
    _redis_client = None
    _token = None

    def check_origin(self, origin):
        return True

    @tornado.gen.coroutine
    def subscribe_redis_channel(self):
        self._redis_client = tornadoredis.Client()
        self._redis_client.connect()
        # subscribe to private__profile_hash channel
        print('private_%s' % self._profile_hash)
        yield tornado.gen.Task(self._redis_client.subscribe, 'private_%s' % self._profile_hash)
        self._redis_client.listen(self.on_redis_message)

    def open(self, token):
        # find user by his token in redis
        self._token = token
        self._profile_hash = redis_client.get(self._token).decode("utf-8")

        if not self._profile_hash:
            # logger.debug("can't find token %s in redis" % self._token)
            # Посылаем клиенту сообщение, что доступ закрыт клиенту
            self.write_message("Access denied")
            self.close()
            return

        logger.debug("WebSocket PrivateInfo on_open")
        self.subscribe_redis_channel()
        # logger.debug("WebSocket experience opened for profile_hash: %s", self._profile_hash)

    def on_redis_message(self, message):
        if message.kind == 'message':
            self.write_message(message.body)

    @tornado.gen.coroutine
    def on_close(self):
        logger.debug("PrivateInfo redis_client connection for user: %s before -------------- %s" %
                     (self._profile_hash, self._redis_client.connection.connected()))
        yield tornado.gen.Task(self._redis_client.unsubscribe, 'private_%s' % self._profile_hash)
        self._redis_client.disconnect()
        logger.debug("PrivateInfo redis_client connection for user: %s after --------------- %s" %
                     (self._profile_hash, self._redis_client.connection.connected()))
        logger.debug("PrivateInfo on_close for user: %s  ", self._profile_hash)


application = tornado.web.Application([
    (r'/public/(?P<token>\w+)/?', PublicInfo),
    (r'/private/(?P<token>\w+)/?', PrivateInfo),
])

if __name__ == "__main__":
    logger.info("server started ...")
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port=PORT, address=SERVER)
    # start loop
    tornado.ioloop.IOLoop.instance().start()
