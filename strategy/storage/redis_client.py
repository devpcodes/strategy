# -*- coding: utf-8 -*-
"""Redis 連線（單例）。"""
import redis
from strategy.config import REDIS_URL

_client = None

def get_redis():
    global _client
    if _client is None:
        _client = redis.from_url(REDIS_URL, decode_responses=True)
    return _client
