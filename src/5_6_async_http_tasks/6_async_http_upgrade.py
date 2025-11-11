import asyncio
import json
from asyncio import Queue
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import aiofiles
from aiohttp import ClientError, ClientSession, ClientTimeout

process_pool = ProcessPoolExecutor(max_workers=2)  # 2 процесса - парсинг и сериализация


def parse_and_serialize(url: str, body: bytes) -> str | None:
    """Парсит JSON и возвращает готовую строку JSONL."""
    try:
        content = json.loads(body)
        result = {"url": url, "content": content}
        return json.dumps(result, ensure_ascii=False) + "\n"
    except Exception:
        return None  # для пропуска


async def write_line(file_path: Path, line: str):
    """Асинхронная запись одной строки."""
    async with aiofiles.open(file_path, "a", encoding="utf-8") as f:
        await f.write(line)


async def consumer(queue: Queue, session: ClientSession, output_file: Path):
    loop = asyncio.get_event_loop()

    while True:
        url = await queue.get()
        if url is None:
            queue.task_done()
            break

        try:
            async with session.get(url) as response:
                if response.status != 200:
                    queue.task_done()
                    continue

                body = await response.read()

                # парсинг и сериализация внутри процесса
                jsonl_line = await loop.run_in_executor(
                    process_pool, parse_and_serialize, url, body
                )

                if jsonl_line:
                    await write_line(output_file, jsonl_line)

        except (ClientError, asyncio.TimeoutError):
            pass
        except Exception:
            pass

        queue.task_done()


async def producer(queue: Queue, input_file: Path):
    async with aiofiles.open(input_file, "r", encoding="utf-8") as f:
        async for line in f:
            url = line.strip()
            if url:
                await queue.put(url)
    # завершаем
    for _ in range(5):
        await queue.put(None)


async def fetch_urls(input_file: Path, output_file: Path):
    queue = asyncio.Queue(maxsize=100)

    timeout = ClientTimeout(
        total=None,
        sock_connect=30,
        sock_read=600,
    )

    async with ClientSession(timeout=timeout) as session:
        # запускаем продюсер
        producer_task = asyncio.create_task(producer(queue, input_file))

        # запускаем консюмеры
        consumers = [
            asyncio.create_task(consumer(queue, session, output_file)) for _ in range(5)
        ]

        await producer_task
        await queue.join()
        await asyncio.gather(*consumers)


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    input_file = script_dir / "urls.txt"
    output_file = script_dir / "update_task_result.jsonl"

    if output_file.exists():
        output_file.unlink()

    asyncio.run(fetch_urls(input_file, output_file))
    print("Файл update_task_result.jsonl готов")
