"""
core/ring.py

Ring buffer implementation for backpressure and decimation.

Usage:
  from core.ring import Ring
  r = Ring(capacity=1000)
  r.push(data)
  all_data = r.pop_all()
"""
from collections import deque


class Ring:
    def __init__(self, capacity: int):
        self.q = deque(maxlen=capacity)

    def push(self, x):
        self.q.append(x)

    def pop_all(self):
        out, self.q = list(self.q), deque(maxlen=self.q.maxlen)
        return out

    def __len__(self):
        return len(self.q)

    @property
    def capacity(self):
        return self.q.maxlen