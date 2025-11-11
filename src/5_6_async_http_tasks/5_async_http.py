import asyncio
import json
from asyncio import Semaphore
from pathlib import Path

import aiofiles
from aiohttp import ClientError, ClientSession, ClientTimeout


async def fetch_one(session: ClientSession, url: str, semaphore: Semaphore):
    """Функция для обработки каждого url"""
    async with semaphore:
        try:
            async with session.get(url) as response:
                return url, response.status
        except (ClientError, asyncio.TimeoutError):
            return url, 0
        except Exception:
            return url, 0


async def write_to_json(file_path: Path, urls: list[str], result: dict[str, int]):
    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        for u in urls:
            line = (
                json.dumps(
                    {"url": u, "status_code": result.get(u, 0)}, ensure_ascii=False
                )
                + "\n"
            )
            await f.write(line)


async def fetch_urls(urls: list[str], file_path: Path):
    """Основная функция с сессией и тасками"""
    semaphore = Semaphore(5)
    async with ClientSession(timeout=ClientTimeout(10)) as session:
        tasks = [
            asyncio.create_task(fetch_one(session, url, semaphore)) for url in urls
        ]
        pairs = await asyncio.gather(*tasks)

    result: dict[str, int] = {u: code for u, code in pairs}

    await write_to_json(file_path, urls, result)


if __name__ == "__main__":
    urls = [
        "https://dzen.ru",
        "https://www.google.com",
        "https://example.com",
        "https://httpbin.org/status/404",
        "https://nonexistent.url",
    ]

    parent_path = Path(__file__).parent
    file_path = parent_path / "results.jsonl"

    if not file_path.exists():
        file_path.touch(exist_ok=True)

    asyncio.run(fetch_urls(urls, file_path))
    print("Файл result.jsonl готов")
