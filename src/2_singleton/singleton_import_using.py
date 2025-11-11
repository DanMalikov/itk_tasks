from singleton_import import user

if __name__ == "__main__":
    obj1 = user
    obj2 = user
    assert obj1 is obj2
