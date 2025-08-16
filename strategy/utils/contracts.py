# -*- coding: utf-8 -*-
"""合約工具：解析主力合約、合成 Redis key 等（保留擴充空間）。"""
def table_of(symbol: str) -> str:
    return "ticks_MXF" if symbol.startswith("MXF") else "ticks_TXF"
