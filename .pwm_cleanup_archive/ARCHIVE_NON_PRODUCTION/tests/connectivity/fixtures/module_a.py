from dataclasses import dataclass


@dataclass
class A:
    value: int


def foo(x):
    return x + 1
