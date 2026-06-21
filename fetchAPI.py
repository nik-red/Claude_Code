"""Fetch data from APIs and save to timestamped directories with logging."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

import httpx


DATA_URLS: list[str] = [
    "https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/dim_customer.csv",
    "https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/dim_store.csv",
    "https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/dim_date.csv",
    "https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/dim_product.csv",
    "https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/fact_sales.csv",
    "https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/fact_returns.csv",
]

BASE_DATA_PATH: Path = Path(".claude/skills/fetchAPI/data")
BASE_LOGS_PATH: Path = Path(".claude/skills/fetchAPI/logs")


def setupLogger(logPath: Path) -> logging.Logger:
    """Set up logger for API fetch operations."""
    logPath.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("fetchAPI")
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(logPath)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


async def fetchData(client: httpx.AsyncClient, url: str) -> tuple[str, bytes | None, str | None]:
    """Fetch data from a single URL."""
    fileName = url.split("/")[-1]
    try:
        response = await client.get(url, timeout=30.0)
        response.raise_for_status()
        return fileName, response.content, None
    except httpx.HTTPError as e:
        return fileName, None, f"HTTP error: {str(e)}"
    except Exception as e:
        return fileName, None, f"Unexpected error: {str(e)}"


async def fetchAllData(logger: logging.Logger) -> None:
    """Fetch data from all URLs concurrently."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dataPath = BASE_DATA_PATH / timestamp
    dataPath.mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting API fetch at {timestamp}")
    logger.info(f"Data will be saved to: {dataPath}")

    async with httpx.AsyncClient() as client:
        tasks = [fetchData(client, url) for url in DATA_URLS]
        results = await asyncio.gather(*tasks)

    successful = 0
    failed = 0

    for fileName, content, error in results:
        if error:
            logger.error(f"Failed to fetch {fileName}: {error}")
            failed += 1
        else:
            filePath = dataPath / fileName
            filePath.write_bytes(content)
            logger.info(f"Successfully fetched and saved {fileName}")
            successful += 1

    logger.info(f"Fetch completed: {successful} successful, {failed} failed")


def main() -> None:
    """Main entry point."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logPath = BASE_LOGS_PATH / timestamp / "fetchAPI.log"

    logger = setupLogger(logPath)

    try:
        asyncio.run(fetchAllData(logger))
    except Exception as e:
        logger.error(f"Fatal error during fetch: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
