"""Singleton через метакласс"""


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Myclass(metaclass=SingletonMeta):
    pass


if __name__ == "__main__":
    obj1 = Myclass()
    obj2 = Myclass()
    assert obj1 is obj2
