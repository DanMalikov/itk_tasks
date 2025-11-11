from datetime import datetime, timezone


class DatetimeMeta(type):
    def __new__(cls, name, bases, attrs):
        attrs["created_at"] = datetime.now(timezone.utc)
        return super().__new__(cls, name, bases, attrs)


class User(metaclass=DatetimeMeta):
    def __init__(self, name):
        self.name = name


if __name__ == "__main__":
    user = User("Bob")

    assert hasattr(user, "created_at")
