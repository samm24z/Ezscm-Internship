#!/usr/bin/env python3
"""
Simple calculator tool for addition and multiplication.
Also exposes a safe_eval for basic 'a op b' forms for demo.
"""

import operator
import re
from typing import Tuple

OPS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "x": operator.mul,
    "×": operator.mul,
    "/": operator.truediv,
}

NUM_OP_NUM = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*([+\-*/x×])\s*(-?\d+(?:\.\d+)?)\s*$")

def parse_simple(expr: str) -> Tuple[float, str, float]:
    m = NUM_OP_NUM.match(expr.strip().lower())
    if not m:
        raise ValueError("Unsupported expression format. Use like '12 * 7'")
    a, op, b = m.groups()
    return float(a), op, float(b)

def calculate(expr: str) -> float:
    a, op, b = parse_simple(expr)
    func = OPS.get(op)
    if not func:
        raise ValueError(f"Unsupported operator: {op}")
    return func(a, b)

def add(a: float, b: float) -> float:
    return a + b

def multiply(a: float, b: float) -> float:
    return a * b
