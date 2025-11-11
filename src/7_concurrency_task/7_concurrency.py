import json
import random
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, Process, Queue, cpu_count


def generate_data(n):
    """Генерация чисел"""
    return [random.randint(1, 1000) for _ in range(n)]


def process_number(x):
    """Функция, выполняющая вычисления над числом"""
    if x < 2:
        return False
    for i in range(2, int(x**0.5) + 1):
        if x % i == 0:
            return False
    return True


def single_thread(data):
    """Однопоточное исполнение"""
    start = time.time()
    list(map(process_number, data))
    return time.time() - start


def thread_pool(data):
    """Реализация с пулом потоков"""
    start = time.time()
    with ThreadPoolExecutor() as pool:
        list(pool.map(process_number, data))
    return time.time() - start


def multiprocessing_pool(data):
    """Реализация multiprocessing.Pool"""
    start = time.time()
    with Pool(processes=cpu_count()) as pool:
        list(pool.map(process_number, data))
    return time.time() - start


def worker(input_queue, output_queue):
    """Воркер для очередей"""
    while True:
        num = input_queue.get()
        if num is None:
            break
        output_queue.put(process_number(num))


def queue_process_based(data):
    """Реализация queue + process"""
    input_queue = Queue()
    output_queue = Queue()
    procs = [
        Process(target=worker, args=(input_queue, output_queue))
        for _ in range(cpu_count())
    ]  # запуск

    for p in procs:
        p.start()

    for num in data:  # запустили очередь
        input_queue.put(num)

    for _ in range(cpu_count()):  # сигнал завершения
        input_queue.put(None)

    start = time.time()
    for _ in range(len(data)):
        output_queue.get()

    for p in procs:
        p.join()
    return time.time() - start


def main():
    n = 100000
    data = generate_data(n)

    timings = [
        ("Single Thread", single_thread(data)),
        ("Thread Pool", thread_pool(data)),
        ("Process Pool", multiprocessing_pool(data)),
        ("Queue-based", queue_process_based(data)),
    ]

    # сохранение таблицы со временем
    result = [
        {"method": name, "time_seconds": round(time_val, 4)}
        for name, time_val in timings
    ]

    with open("multiprocessing_results.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()
