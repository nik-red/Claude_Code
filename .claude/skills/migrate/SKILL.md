---
name: migrate
description: Migrates the fetched data stored in the ".claude/skills/fetchAPI/data/" directory to a new location. Use when you want to move your data to a different directory. 
--- 


## Usage

### Step-1: Pick the python environment
Before you start, make sure to pick the python environment in which you want to run the code. You can run/install dependencies using my '.venv' environment which is located at "C:\ClaudeCode\.venv"

### Step-2: Run the Python Script To Migrate Data
- You need to run the Python Script stored at ".claude/skills/migrate/scripts/convert_to_parquet.py".

## Features

- **CSV to Parquet Conversion**: Converts all CSV files from the latest dated folder in `.claude/skills/fetchAPI/data/` to Parquet format for better compression and performance.
- **Automatic Logging**: Generates a detailed migration log as a CSV file containing:
  - Timestamp of conversion
  - Source and output filenames
  - Conversion status (SUCCESS/FAILED)
  - Data shape (rows and columns)
  - Output file size in KB
  - Error messages (if any)

## Output

- **Converted Files**: All `.parquet` files are saved in `.claude/skills/migrate/data/<datetime_folder>/`
- **Migration Logs**: A CSV log file named `migration_logs_YYYY-MM-DD_HH-MM-SS.csv` is saved in `.claude/skills/migrate/data/`