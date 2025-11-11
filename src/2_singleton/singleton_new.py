"""Singleton в дандер методе new"""


class Myclass:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, name: str, age: int):
        if not hasattr(self, "initialized"):
            self.name = name
            self.age = age
            self.initialized = True


if __name__ == "__main__":
    alex = Myclass("Alex", 20)
    john = Myclass("John", 30)

    assert alex is john
    assert alex.name == john.name
