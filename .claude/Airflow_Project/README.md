# Airflow Project

## Overview

This Airflow project implements a data pipeline with **data-aware scheduling**. It consists of two orchestrated DAGs that demonstrate producer-consumer patterns using Apache Airflow's asset-based dependencies.

---

## Project Structure

```
Airflow_Project/
├── dags/
│   ├── data_fetch.py      # Producer DAG - fetches and materializes weather data
│   └── data_report.py     # Consumer DAG - reads and analyzes weather data
└── README.md              # This file
```

---

## DAGs Overview

### 1. `data_fetch.py` (Producer DAG)

**Purpose:** Fetch weather data, transform it, and materialize it as a persistent asset.

**Workflow:**
1. **prepare_storage()** - Creates the `/opt/airflow/data` directory to store output files
2. **fetch_api_data()** - Simulates an API call to fetch weather data (returns city, temperature, unit)
3. **transform_data()** - Cleanses the raw data by adding:
   - `processed_at`: Timestamp of processing
   - `status`: Data quality indicator
4. **materialize_asset()** - Writes the final data to `/opt/airflow/data/weather_report.json` and registers it as a persistent asset

**Key Feature:** Uses Airflow's asset outlet (`outlets=[weather_data_asset]`) to declare that this DAG produces a data asset that other DAGs can depend on.

---

### 2. `data_report.py` (Consumer DAG)

**Purpose:** Consume the weather data asset and generate analytical reports.

**Workflow:**
1. **read_asset()** - Reads the materialized asset (`weather_report.json`)
2. Analyzes and prints the weather data (city, temperature)

**Key Feature:** Uses `schedule=[weather_data_asset]` to make this DAG automatically trigger when the `weather_data_asset` from `data_fetch` is produced.

---

## Data Flow

```
data_fetch DAG                          data_report DAG
    ↓                                         ↑
prepare_storage                          read_asset
    ↓                                         ↑
fetch_api_data                          (triggered by)
    ↓                                    weather_data_asset
transform_data                               ↑
    ↓                                         │
materialize_asset                            │
    ↓ (outlets)                              │
weather_report.json ────────────────────────┘
(Asset File)
```

---

## Setup & Requirements

### Prerequisites
- Apache Airflow 2.7+ (SDK 1.0+)
- Python 3.10+
- Storage directory: `/opt/airflow/data` (created automatically by the DAG)

### Installation

1. **Install Airflow:**
   ```bash
   pip install apache-airflow
   ```

2. **Enable Asset-Based Scheduling:**
   Ensure your Airflow configuration supports asset-based scheduling in `airflow.cfg`:
   ```
   [scheduler]
   enable_asset_triggered_dag = True
   ```

3. **Place DAGs:**
   Copy the DAGs to your Airflow `dags/` folder:
   ```bash
   cp dags/*.py $AIRFLOW_HOME/dags/
   ```

---

## Running the Project

### Start Airflow

```bash
# Initialize the Airflow database
airflow db init

# Start the webserver
airflow webserver --port 8080

# In another terminal, start the scheduler
airflow scheduler
```

### Trigger DAGs

1. **Manual Trigger (data_fetch):**
   ```bash
   airflow dags trigger data_fetch
   ```

2. **Automatic Trigger (data_report):**
   Once `data_fetch` completes, `data_report` will be automatically scheduled and triggered due to the asset dependency.

### Monitor Execution

Visit the Airflow UI at `http://localhost:8080` to:
- View DAG execution history
- Monitor task status
- Check asset dependencies in the Graph view

---

## Output

When both DAGs execute successfully, you'll see:

1. **File Created:** `/opt/airflow/data/weather_report.json`
   ```json
   {
     "city": "New York",
     "temp": 22,
     "unit": "C",
     "processed_at": "2026-06-21T10:30:45.123456",
     "status": "cleansed"
   }
   ```

2. **Console Output:** 
   ```
   Analyzing data for New York: 22°C
   ```

---

## Key Concepts

### Asset-Based Scheduling (Data-Aware Scheduling)
- **Producer (data_fetch):** Declares an outlet asset that it materializes
- **Consumer (data_report):** Depends on the asset as a scheduling trigger
- **Benefit:** DAGs automatically trigger based on data availability, not time-based schedules

### Decorator-Based DAGs
Both DAGs use Airflow's modern `@dag` and `@task` decorators for cleaner, more Pythonic code compared to traditional operator-based DAGs.

---

## Future Enhancements

- Replace simulated API with real weather API (e.g., OpenWeatherMap)
- Add error handling and retries
- Implement data validation tasks
- Add email notifications on pipeline completion
- Store data in databases instead of JSON files
- Create downstream DAGs for visualization and reporting

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'data_fetch'` | Ensure both DAG files are in the `dags/` folder |
| `data_report` doesn't trigger automatically | Check that `enable_asset_triggered_dag = True` in `airflow.cfg` |
| Permission denied on `/opt/airflow/data` | Ensure the Airflow process has write permissions to the directory |

---

## Contributing

- Follow PEP 8 and PEP 257 standards for Python code
- Add type hints to all functions
- Test DAGs locally before deploying
- Document any changes in this README

---

*Last Updated: 2026-06-21*
