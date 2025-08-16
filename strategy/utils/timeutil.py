# -*- coding: utf-8 -*-
"""時間工具（預留未來擴充）。"""
from datetime import datetime

def minute_floor(ts: datetime) -> datetime:
    return ts.replace(second=0, microsecond=0)
