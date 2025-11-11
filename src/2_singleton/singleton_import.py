"""Singleton, вызываемый через импорт"""

from dataclasses import dataclass

_instance = None


@dataclass(frozen=True)
class User:
    name: str
    age: int


def __getattr__(name: str):
    global _instance
    if name == "user":
        if _instance is None:
            _instance = User("Alex", 22)
        return _instance
    raise AttributeError(name)
