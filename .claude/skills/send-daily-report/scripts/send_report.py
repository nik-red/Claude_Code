"""
Send daily data analysis report via email.

This script:
1. Reads data from migration directory
2. Calculates key metrics from sales and returns data
3. Generates a professional HTML email report
4. Sends via SMTP with error handling
"""

import os
import sys
import logging
import smtplib
import pandas as pd
from datetime import datetime
from pathlib import Path
from html import escape
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import TypedDict

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class SmtpConfig(TypedDict):
    """SMTP configuration type definition."""

    server: str
    port: int
    sender_email: str
    sender_password: str
    manager_email: str


class MetricsDict(TypedDict):
    """Metrics data type definition."""

    total_sales: float
    total_returns: float
    net_sales: float
    return_rate: float
    top_product: str
    top_product_sales: float
    top_customer: str
    top_customer_sales: float
    top_store: str
    top_store_sales: float
    top_return_product: str
    top_return_product_amount: float
    highest_return_store: str
    highest_return_amount: float
    num_sales_records: int
    num_return_records: int


def loadEnvironmentVariables() -> SmtpConfig:
    """
    Load and validate SMTP configuration from environment.

    Returns:
        SMTP configuration dictionary.

    Raises:
        ValueError: If any required environment variable is missing.
    """
    required_vars = ["SMTP_SERVER", "SMTP_PORT", "SENDER_EMAIL", "SENDER_PASSWORD", "MANAGER_EMAIL"]
    config: dict[str, str | int] = {}

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise ValueError(f"Missing environment variable: {var}")
        config[var] = value

    try:
        config["SMTP_PORT"] = int(config["SMTP_PORT"])
    except ValueError:
        raise ValueError("SMTP_PORT must be an integer")

    logger.info("SMTP configuration loaded successfully")
    return SmtpConfig(
        server=str(config["SMTP_SERVER"]),
        port=int(config["SMTP_PORT"]),
        sender_email=str(config["SENDER_EMAIL"]),
        sender_password=str(config["SENDER_PASSWORD"]),
        manager_email=str(config["MANAGER_EMAIL"])
    )


def loadData(data_dir_path: str | None = None) -> tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame
]:
    """
    Load parquet files from migration directory.

    Args:
        data_dir_path: Path to data directory. Uses env var if None.

    Returns:
        Tuple of (dim_customer, dim_date, dim_product, dim_store, fact_sales, fact_returns).

    Raises:
        FileNotFoundError: If data directory or files not found.
        RuntimeError: If data loading fails.
    """
    if data_dir_path is None:
        data_dir_path = os.getenv(
            "DATA_DIR",
            r"c:\ClaudeCode\.claude\skills\migrate\data\2026-06-05_08-35-07"
        )

    data_dir = Path(data_dir_path)
    logger.info(f"Loading data from {data_dir}")

    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    try:
        dim_customer = pd.read_parquet(data_dir / "dim_customer.parquet")
        dim_date = pd.read_parquet(data_dir / "dim_date.parquet")
        dim_product = pd.read_parquet(data_dir / "dim_product.parquet")
        dim_store = pd.read_parquet(data_dir / "dim_store.parquet")
        fact_sales = pd.read_parquet(data_dir / "fact_sales.parquet")
        fact_returns = pd.read_parquet(data_dir / "fact_returns.parquet")

        logger.info("Data loaded successfully!")
        logger.info(f"Sales records: {len(fact_sales)}")
        logger.info(f"Returns records: {len(fact_returns)}")

        return dim_customer, dim_date, dim_product, dim_store, fact_sales, fact_returns
    except FileNotFoundError as e:
        logger.error(f"Missing parquet file: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        raise RuntimeError(f"Failed to load data: {str(e)}")


def calculateMetrics(
    dim_customer: pd.DataFrame,
    dim_product: pd.DataFrame,
    dim_store: pd.DataFrame,
    fact_sales: pd.DataFrame,
    fact_returns: pd.DataFrame
) -> MetricsDict:
    """
    Calculate key metrics from the data.

    Args:
        dim_customer: Customer dimension table.
        dim_product: Product dimension table.
        dim_store: Store dimension table.
        fact_sales: Sales fact table.
        fact_returns: Returns fact table.

    Returns:
        Dictionary containing calculated metrics.

    Raises:
        ValueError: If data is empty or aggregation fails.
    """
    logger.info("Calculating metrics")

    if fact_sales.empty:
        raise ValueError("Sales data is empty")
    if fact_returns.empty:
        raise ValueError("Returns data is empty")

    total_sales = float(fact_sales["net_amount"].sum())
    total_returns = float(fact_returns["refund_amount"].sum())
    net_sales = total_sales - total_returns
    return_rate = (total_returns / total_sales * 100) if total_sales > 0 else 0.0

    sales_data = fact_sales.merge(dim_product, on="product_sk", how="left")
    sales_data = sales_data.merge(dim_store, on="store_sk", how="left")
    sales_data = sales_data.merge(dim_customer, on="customer_sk", how="left")

    returns_data = fact_returns.merge(dim_product, on="product_sk", how="left")
    returns_data = returns_data.merge(dim_store, on="store_sk", how="left")

    product_sales = sales_data.groupby("product_name")["net_amount"].sum()
    if product_sales.empty:
        raise ValueError("No product sales found")

    top_product = str(product_sales.idxmax())
    top_product_sales = float(product_sales.max())

    customer_sales = sales_data.groupby("last_name")["net_amount"].sum()
    if customer_sales.empty:
        raise ValueError("No customer sales found")

    top_customer = str(customer_sales.idxmax())
    top_customer_sales = float(customer_sales.max())

    store_sales = sales_data.groupby("store_name")["net_amount"].sum()
    if store_sales.empty:
        raise ValueError("No store sales found")

    top_store = str(store_sales.idxmax())
    top_store_sales = float(store_sales.max())

    product_returns = returns_data.groupby("product_name")["refund_amount"].sum()
    if product_returns.empty:
        raise ValueError("No product returns found")

    top_return_product = str(product_returns.idxmax())
    top_return_product_amount = float(product_returns.max())

    store_returns = returns_data.groupby("store_name")["refund_amount"].sum()
    if store_returns.empty:
        raise ValueError("No store returns found")

    highest_return_store = str(store_returns.idxmax())
    highest_return_amount = float(store_returns.max())

    return MetricsDict(
        total_sales=total_sales,
        total_returns=total_returns,
        net_sales=net_sales,
        return_rate=return_rate,
        top_product=top_product,
        top_product_sales=top_product_sales,
        top_customer=top_customer,
        top_customer_sales=top_customer_sales,
        top_store=top_store,
        top_store_sales=top_store_sales,
        top_return_product=top_return_product,
        top_return_product_amount=top_return_product_amount,
        highest_return_store=highest_return_store,
        highest_return_amount=highest_return_amount,
        num_sales_records=len(fact_sales),
        num_return_records=len(fact_returns),
    )


def generateHtmlEmail(metrics: MetricsDict, report_time: datetime) -> str:
    """
    Generate professional HTML email content.

    Args:
        metrics: Dictionary of calculated metrics.
        report_time: Datetime when report was generated.

    Returns:
        HTML string for email body.
    """
    logger.info("Generating HTML report")

    time_str = report_time.strftime('%B %d, %Y at %I:%M %p')
    health_status = 'healthy' if metrics['return_rate'] < 5 else 'monitor closely'

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .header {{
                border-bottom: 3px solid #2563eb;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                margin: 0;
                color: #1f2937;
                font-size: 28px;
            }}
            .timestamp {{
                color: #6b7280;
                font-size: 14px;
                margin-top: 5px;
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }}
            .metric-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 6px;
                text-align: center;
            }}
            .metric-card.sales {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}
            .metric-card.returns {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            }}
            .metric-card.net {{
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            }}
            .metric-card.rate {{
                background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            }}
            .metric-value {{
                font-size: 24px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .metric-label {{
                font-size: 14px;
                opacity: 0.9;
            }}
            .section {{
                margin-bottom: 30px;
            }}
            .section h2 {{
                color: #1f2937;
                border-left: 4px solid #2563eb;
                padding-left: 15px;
                margin-bottom: 15px;
                font-size: 18px;
            }}
            .insight {{
                background-color: #f0f4ff;
                padding: 15px;
                border-left: 4px solid #2563eb;
                margin-bottom: 12px;
                border-radius: 4px;
            }}
            .insight-title {{
                font-weight: bold;
                color: #2563eb;
                margin-bottom: 5px;
            }}
            .insight-value {{
                color: #1f2937;
            }}
            .footer {{
                border-top: 1px solid #e5e7eb;
                padding-top: 20px;
                margin-top: 30px;
                font-size: 12px;
                color: #6b7280;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Daily Data Analysis Report</h1>
                <div class="timestamp">Generated on {time_str}</div>
            </div>

            <div class="section">
                <h2>📈 Executive Summary</h2>
                <div class="metrics-grid">
                    <div class="metric-card sales">
                        <div class="metric-label">Total Sales</div>
                        <div class="metric-value">${metrics['total_sales']:,.2f}</div>
                    </div>
                    <div class="metric-card returns">
                        <div class="metric-label">Total Returns</div>
                        <div class="metric-value">${metrics['total_returns']:,.2f}</div>
                    </div>
                    <div class="metric-card net">
                        <div class="metric-label">Net Sales</div>
                        <div class="metric-value">${metrics['net_sales']:,.2f}</div>
                    </div>
                    <div class="metric-card rate">
                        <div class="metric-label">Return Rate</div>
                        <div class="metric-value">{metrics['return_rate']:.2f}%</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🎯 Sales Performance</h2>
                <div class="insight">
                    <div class="insight-title">🏆 Top Performing Product</div>
                    <div class="insight-value">{escape(metrics['top_product'])} — ${metrics['top_product_sales']:,.2f}</div>
                </div>
                <div class="insight">
                    <div class="insight-title">⭐ Top Customer</div>
                    <div class="insight-value">{escape(metrics['top_customer'])} — ${metrics['top_customer_sales']:,.2f} in purchases</div>
                </div>
                <div class="insight">
                    <div class="insight-title">🏪 Top Store</div>
                    <div class="insight-value">{escape(metrics['top_store'])} — ${metrics['top_store_sales']:,.2f}</div>
                </div>
                <div class="insight">
                    <div class="insight-title">📊 Transaction Volume</div>
                    <div class="insight-value">{metrics['num_sales_records']:,} sales transactions processed</div>
                </div>
            </div>

            <div class="section">
                <h2>⚠️ Returns Analysis</h2>
                <div class="insight">
                    <div class="insight-title">📦 Highest Return Product</div>
                    <div class="insight-value">{escape(metrics['top_return_product'])} — ${metrics['top_return_product_amount']:,.2f} returned</div>
                </div>
                <div class="insight">
                    <div class="insight-title">🛑 Highest Return Store</div>
                    <div class="insight-value">{escape(metrics['highest_return_store'])} — ${metrics['highest_return_amount']:,.2f} in returns</div>
                </div>
                <div class="insight">
                    <div class="insight-title">📈 Return Transactions</div>
                    <div class="insight-value">{metrics['num_return_records']} return transactions</div>
                </div>
                <div class="insight">
                    <div class="insight-title">💡 Key Observation</div>
                    <div class="insight-value">Return rate is {metrics['return_rate']:.2f}% — {health_status}. Focus on {escape(metrics['top_return_product'])} quality and {escape(metrics['highest_return_store'])} operations.</div>
                </div>
            </div>

            <div class="section">
                <h2>✅ Action Items</h2>
                <div class="insight">
                    <div class="insight-value">
                        1. Review quality control for {escape(metrics['top_return_product'])}<br/>
                        2. Investigate {escape(metrics['highest_return_store'])} return trends<br/>
                        3. Recognize {escape(metrics['top_customer'])} as top customer<br/>
                        4. Analyze {escape(metrics['top_product'])} success factors
                    </div>
                </div>
            </div>

            <div class="footer">
                <p>This is an automated daily report generated by the Data Analysis System. For detailed visualizations and analysis, check the visualization dashboard.</p>
                <p>Questions or issues? Contact the data team.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return html


def sendEmail(config: SmtpConfig, html_content: str, report_time: datetime) -> None:
    """
    Send email via SMTP.

    Args:
        config: SMTP configuration.
        html_content: HTML content for email body.
        report_time: Datetime when report was generated.

    Raises:
        RuntimeError: If email sending fails.
    """
    logger.info(f"Sending email to {config['manager_email']}")

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Daily Data Analysis Report — {report_time.strftime('%B %d, %Y')}"
        msg["From"] = config["sender_email"]
        msg["To"] = config["manager_email"]

        part = MIMEText(html_content, "html")
        msg.attach(part)

        with smtplib.SMTP(config["server"], config["port"]) as server:
            server.starttls()
            server.login(config["sender_email"], config["sender_password"])
            server.send_message(msg)

        logger.info(f"Report sent successfully to {config['manager_email']}")

    except smtplib.SMTPAuthenticationError as e:
        logger.error("SMTP authentication failed. Verify credentials in environment variables.")
        raise RuntimeError("SMTP authentication failed") from e
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {str(e)}")
        raise RuntimeError(f"SMTP error occurred: {str(e)}") from e
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise RuntimeError(f"Failed to send email: {str(e)}") from e


def main() -> None:
    """Main execution function."""
    try:
        logger.info("Starting daily report generation")

        report_time = datetime.now()

        config = loadEnvironmentVariables()

        dim_customer, dim_date, dim_product, dim_store, fact_sales, fact_returns = loadData()

        metrics = calculateMetrics(dim_customer, dim_product, dim_store, fact_sales, fact_returns)

        html_content = generateHtmlEmail(metrics, report_time)

        sendEmail(config, html_content, report_time)

        logger.info("Daily report process completed successfully!")

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"[ERROR] {str(e)}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
