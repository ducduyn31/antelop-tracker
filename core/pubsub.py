import json
import os

import redis

from utils import Singleton


class PubSub:

    def __init__(self, connection_uri: str):
        host, port, db = self.__parse_connection_uri(connection_uri)
        self._host = host
        self._port = port
        self._db = db
        self._redis = redis.Redis(host=host, port=port, db=db)

        pubsub_config = self._redis.config_get('notify-keyspace-events')
        if 'K' not in pubsub_config or 'E' not in pubsub_config or 'A' not in pubsub_config:
            self._redis.config_set('notify-keyspace-events', 'KEA')
        self._pubsub = self._redis.pubsub()

    def subscribe(self, key_event, callback):
        self._pubsub.subscribe(**{f'__keyevent@{self._db}__:{key_event}': callback})
        self._pubsub.run_in_thread(sleep_time=.01)

    def publish_time_event(self, key, expire):
        self._redis.set(key, "", ex=expire)

    @staticmethod
    def __parse_connection_uri(uri: str):
        _uri = uri
        if uri.startswith('redis://'):
            _uri = uri[8:]

        host, port_and_db = _uri.split(':')[0], _uri.split(':')[1]

        if '/' in port_and_db:
            port, db = port_and_db.split('/')[0], port_and_db.split('/')[1]
        else:
            port = port_and_db
            db = 0

        return host, port, db
