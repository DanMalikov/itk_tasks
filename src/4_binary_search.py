def bin_s(array: list, target: int) -> bool:
    low = 0
    high = len(array) - 1
    while low <= high:
        mid = (low + high) // 2
        value = array[mid]
        if value == target:
            return True
        if value < target:
            low = mid + 1
        else:
            high = mid - 1

    return False


if __name__ == "__main__":
    operation1 = bin_s([1, 2, 3, 45, 356, 569, 600, 705, 923], 20)
    operation2 = bin_s([3, 9, 10, 11, 12, 13, 14, 17, 18, 19], 10)

    assert not operation1
    assert operation2
