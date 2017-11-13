# -*- coding: UTF-8 -*-

from taxiProject.redis_connection import redis_conn
from django.conf import settings
import hashlib


class RedisSetKeyMiddleware(object):

    def process_request(self, request):
        """
        Установка ключа в редис
        """
        if redis_conn.get(request.session.session_key) is None:
            redis_conn.setex(request.session.session_key, hashlib.sha1(str(request.user.pk).encode('utf-8')).hexdigest(), settings.SESSION_COOKIE_AGE)
