import asyncio
import httpx
import logging
import os
from datetime import datetime
from pathlib import Path

# URLs to fetch
URLS = [
    "https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/dim_customer.csv",
    "https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/dim_store.csv",
    "https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/dim_date.csv",
    "https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/dim_product.csv",
    "https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/fact_sales.csv",
    "https://raw.githubusercontent.com/anshlambagit/AnshLambaYoutube/refs/heads/main/DBT_Masterclass/fact_returns.csv",
]

# Create timestamp
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Setup directories
data_dir = Path(".claude/skills/fetchAPI/data") / timestamp
logs_dir = Path(".claude/skills/fetchAPI/logs") / timestamp

data_dir.mkdir(parents=True, exist_ok=True)
logs_dir.mkdir(parents=True, exist_ok=True)

# Setup logging
log_file = logs_dir / "fetchAPI.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info(f"Starting data fetch at {timestamp}")
logger.info(f"Data will be saved to: {data_dir}")


async def fetch_and_save_data():
    """Fetch data from all URLs and save as CSV files."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        for url in URLS:
            try:
                logger.info(f"Fetching: {url}")
                response = await client.get(url)
                response.raise_for_status()

                # Extract filename from URL
                filename = url.split("/")[-1]
                file_path = data_dir / filename

                # Save file
                with open(file_path, "wb") as f:
                    f.write(response.content)

                logger.info(f"✓ Successfully saved: {filename} ({len(response.content)} bytes)")

            except httpx.TimeoutException:
                logger.error(f"✗ Timeout while fetching: {url}")
            except httpx.HTTPError as e:
                logger.error(f"✗ HTTP Error for {url}: {e}")
            except Exception as e:
                logger.error(f"✗ Error fetching {url}: {e}")

    logger.info("Data fetch completed")


if __name__ == "__main__":
    asyncio.run(fetch_and_save_data())
    logger.info(f"Log file saved to: {log_file}")
