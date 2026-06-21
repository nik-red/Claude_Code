"""
Script to convert CSV files from the latest folder in fetchAPI/data to parquet format.

The files are saved in a folder with the same datetime name as the source folder.
Conversion logs are saved as a CSV file in the migrate folder.
"""

import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import TypedDict

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class ConversionLog(TypedDict):
    """Type definition for conversion log entries."""

    timestamp: str
    source_file: str
    output_file: str | None
    status: str
    rows: int | None
    columns: int | None
    size_kb: float | None
    error: str | None


def getLatestFolder(source_path: str) -> tuple[str, str]:
    """
    Get the latest folder from the source path based on datetime naming.

    Args:
        source_path: Path to the source directory containing datetime-named folders.

    Returns:
        Tuple of (folder_name, full_path) for the latest folder.

    Raises:
        FileNotFoundError: If source path doesn't exist or contains no folders.
    """
    source = Path(source_path)

    if not source.exists():
        raise FileNotFoundError(f"Source path does not exist: {source_path}")

    folders = [d for d in source.iterdir() if d.is_dir()]

    if not folders:
        raise FileNotFoundError(f"No folders found in {source_path}")

    latest_folder = max(folders, key=lambda x: x.name)
    return latest_folder.name, str(latest_folder)


def convertCsvToParquet(
    source_folder: str,
    output_base_path: str,
    folder_name: str
) -> list[ConversionLog]:
    """
    Convert all CSV files in source folder to parquet format.

    Args:
        source_folder: Path to the source folder containing CSV files.
        output_base_path: Base path where output folder will be created.
        folder_name: Name of the datetime folder (used for creating output folder).

    Returns:
        List of log dictionaries containing conversion details.

    Raises:
        FileNotFoundError: If source folder doesn't exist.
    """
    source = Path(source_folder)

    if not source.exists() or not source.is_dir():
        raise FileNotFoundError(f"Source folder does not exist or is not a directory: {source_folder}")

    output_folder = Path(output_base_path) / folder_name
    logs: list[ConversionLog] = []

    output_folder.mkdir(parents=True, exist_ok=True)

    csv_files = list(source.glob("*.csv"))

    if not csv_files:
        logger.warning(f"No CSV files found in {source_folder}")
        return logs

    logger.info(f"Found {len(csv_files)} CSV file(s) in {source_folder}")
    logger.info(f"Output folder: {output_folder}")

    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)

            parquet_filename = csv_file.stem + ".parquet"
            parquet_path = output_folder / parquet_filename

            df.to_parquet(parquet_path, engine="pyarrow", index=False)

            file_size_kb = parquet_path.stat().st_size / 1024
            logger.info(f"Converted {csv_file.name} -> {parquet_filename} (Shape: {df.shape}, Size: {file_size_kb:.2f} KB)")

            logs.append({
                "timestamp": datetime.now().isoformat(),
                "source_file": csv_file.name,
                "output_file": parquet_filename,
                "status": "SUCCESS",
                "rows": df.shape[0],
                "columns": df.shape[1],
                "size_kb": round(file_size_kb, 2),
                "error": None
            })

        except FileNotFoundError as e:
            error_msg = str(e)
            logger.error(f"File not found while converting {csv_file.name}: {error_msg}")
            logs.append({
                "timestamp": datetime.now().isoformat(),
                "source_file": csv_file.name,
                "output_file": None,
                "status": "FAILED",
                "rows": None,
                "columns": None,
                "size_kb": None,
                "error": error_msg
            })

        except pd.errors.ParserError as e:
            error_msg = f"CSV parsing error: {str(e)}"
            logger.error(f"Error parsing {csv_file.name}: {error_msg}")
            logs.append({
                "timestamp": datetime.now().isoformat(),
                "source_file": csv_file.name,
                "output_file": None,
                "status": "FAILED",
                "rows": None,
                "columns": None,
                "size_kb": None,
                "error": error_msg
            })

        except OSError as e:
            error_msg = f"I/O error: {str(e)}"
            logger.error(f"I/O error converting {csv_file.name}: {error_msg}")
            logs.append({
                "timestamp": datetime.now().isoformat(),
                "source_file": csv_file.name,
                "output_file": None,
                "status": "FAILED",
                "rows": None,
                "columns": None,
                "size_kb": None,
                "error": error_msg
            })

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Unexpected error converting {csv_file.name}: {error_msg}")
            logs.append({
                "timestamp": datetime.now().isoformat(),
                "source_file": csv_file.name,
                "output_file": None,
                "status": "FAILED",
                "rows": None,
                "columns": None,
                "size_kb": None,
                "error": error_msg
            })

    return logs


def saveLogsToCsv(logs: list[ConversionLog], output_base_path: str) -> str:
    """
    Save conversion logs to a CSV file.

    Args:
        logs: List of log dictionaries.
        output_base_path: Base path where logs will be saved.

    Returns:
        Path to the saved CSV file.

    Raises:
        OSError: If logs cannot be written to disk.
    """
    output_path = Path(output_base_path)
    output_path.mkdir(parents=True, exist_ok=True)

    log_filename = f"migration_logs_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    log_filepath = output_path / log_filename

    try:
        df_logs = pd.DataFrame(logs)
        df_logs.to_csv(log_filepath, index=False)
        logger.info(f"Logs saved to {log_filepath}")
        return str(log_filepath)
    except OSError as e:
        logger.error(f"Failed to write logs to {log_filepath}: {str(e)}")
        raise


def main() -> None:
    """Orchestrate the CSV to Parquet conversion process."""
    import os

    source_base = os.getenv("FETCHAPI_DATA_DIR", r".\.claude\skills\fetchAPI\data")
    output_base = os.getenv("MIGRATE_DATA_DIR", r".\.claude\skills\migrate\data")

    logger.info("=" * 70)
    logger.info("CSV to Parquet Converter")
    logger.info("=" * 70)

    try:
        latest_folder_name, latest_folder_path = getLatestFolder(source_base)
        logger.info(f"Latest source folder: {latest_folder_name}")
        logger.info(f"Full path: {latest_folder_path}")

        logs = convertCsvToParquet(latest_folder_path, output_base, latest_folder_name)

        if logs:
            log_file = saveLogsToCsv(logs, output_base)
            logger.info(f"Logs saved to: {log_file}")

        logger.info("=" * 70)
        logger.info("Conversion completed successfully!")
        logger.info("=" * 70)

    except FileNotFoundError as e:
        logger.error(f"Error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise


if __name__ == "__main__":
    main()