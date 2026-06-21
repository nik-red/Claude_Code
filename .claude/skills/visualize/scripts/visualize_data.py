"""
Data visualization and KPI analysis script.

Reads parquet files from migration directory and generates KPIs and visualizations
for sales and returns data analysis.
"""

import logging
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Config:
    """Visualization configuration constants."""

    DPI = 300
    BBOX_INCHES = "tight"
    FONT_SIZE_TITLE = 14
    FONT_SIZE_DEFAULT = 10
    FIGSIZE_WIDE = (14, 6)
    FIGSIZE_STANDARD = (12, 6)
    TOP_N_ITEMS = 15

    COLORS = {
        'sales_trend': '#1f77b4',
        'sales_by_store': '#2ca02c',
        'sales_by_product': '#d62728',
        'sales_by_customer': '#ff7f0e',
        'returns_trend': '#d62728',
        'returns_by_store': '#9467bd',
        'returns_by_product': '#8c564b',
        'returns_by_customer': '#e377c2',
    }


def loadDimensionTables(data_dir: Path) -> Dict[str, pd.DataFrame]:
    """
    Load dimension and fact tables from parquet files.

    Args:
        data_dir: Path to directory containing parquet files.

    Returns:
        Dictionary mapping table names to DataFrames.

    Raises:
        FileNotFoundError: If required parquet files are not found.
    """
    logger.info(f"Loading data from {data_dir}")

    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    try:
        tables = {
            'dim_customer': pd.read_parquet(data_dir / "dim_customer.parquet"),
            'dim_date': pd.read_parquet(data_dir / "dim_date.parquet"),
            'dim_product': pd.read_parquet(data_dir / "dim_product.parquet"),
            'dim_store': pd.read_parquet(data_dir / "dim_store.parquet"),
            'fact_sales': pd.read_parquet(data_dir / "fact_sales.parquet"),
            'fact_returns': pd.read_parquet(data_dir / "fact_returns.parquet"),
        }
        logger.info("Data loaded successfully!")
        logger.info(f"Sales records: {len(tables['fact_sales'])}")
        logger.info(f"Returns records: {len(tables['fact_returns'])}")
        return tables
    except FileNotFoundError as e:
        logger.error(f"Missing parquet file: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        raise


def mergeSalesData(
    fact_sales: pd.DataFrame,
    dim_date: pd.DataFrame,
    dim_store: pd.DataFrame,
    dim_product: pd.DataFrame,
    dim_customer: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge fact sales with dimension tables.

    Args:
        fact_sales: Fact sales table.
        dim_date: Date dimension table.
        dim_store: Store dimension table.
        dim_product: Product dimension table.
        dim_customer: Customer dimension table.

    Returns:
        Merged sales data with all dimensions.
    """
    sales_data = fact_sales.merge(dim_date, on="date_sk", how="left")
    sales_data = sales_data.merge(dim_store, on="store_sk", how="left")
    sales_data = sales_data.merge(dim_product, on="product_sk", how="left")
    sales_data = sales_data.merge(dim_customer, on="customer_sk", how="left")
    return sales_data


def mergeReturnsData(
    fact_returns: pd.DataFrame,
    dim_date: pd.DataFrame,
    dim_store: pd.DataFrame,
    dim_product: pd.DataFrame,
    fact_sales: pd.DataFrame,
    dim_customer: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge fact returns with dimension tables.

    Args:
        fact_returns: Fact returns table.
        dim_date: Date dimension table.
        dim_store: Store dimension table.
        dim_product: Product dimension table.
        fact_sales: Fact sales table (for customer info).
        dim_customer: Customer dimension table.

    Returns:
        Merged returns data with all dimensions.
    """
    returns_data = fact_returns.merge(dim_date, on="date_sk", how="left")
    returns_data = returns_data.merge(dim_store, on="store_sk", how="left")
    returns_data = returns_data.merge(dim_product, on="product_sk", how="left")

    customer_info = fact_sales[['sales_id', 'customer_sk']].merge(
        dim_customer, on="customer_sk", how="left"
    )
    returns_data = returns_data.merge(customer_info, on="sales_id", how="left")
    return returns_data


def calculateKpis(
    fact_sales: pd.DataFrame,
    fact_returns: pd.DataFrame,
    sales_data: pd.DataFrame,
    returns_data: pd.DataFrame
) -> Dict[str, float | str]:
    """
    Calculate key performance indicators from sales and returns data.

    Args:
        fact_sales: Fact sales table.
        fact_returns: Fact returns table.
        sales_data: Merged sales data.
        returns_data: Merged returns data.

    Returns:
        Dictionary of calculated KPIs.
    """
    logger.info("Building KPIs")

    total_sales = fact_sales["net_amount"].sum()
    total_returns = fact_returns["refund_amount"].sum()
    net_sales = total_sales - total_returns

    avg_sales_per_store = fact_sales.groupby("store_sk")["net_amount"].sum().mean()
    avg_sales_per_product = fact_sales.groupby("product_sk")["net_amount"].sum().mean()
    avg_sales_per_customer = fact_sales.groupby("customer_sk")["net_amount"].sum().mean()

    logger.info(f"Total Sales: ${total_sales:,.2f}")
    logger.info(f"Total Returns: ${total_returns:,.2f}")
    logger.info(f"Net Sales: ${net_sales:,.2f}")
    logger.info(f"Average Sales per Store: ${avg_sales_per_store:,.2f}")
    logger.info(f"Average Sales per Product: ${avg_sales_per_product:,.2f}")
    logger.info(f"Average Sales per Customer: ${avg_sales_per_customer:,.2f}")

    return {
        'total_sales': total_sales,
        'total_returns': total_returns,
        'net_sales': net_sales,
        'avg_sales_per_store': avg_sales_per_store,
        'avg_sales_per_product': avg_sales_per_product,
        'avg_sales_per_customer': avg_sales_per_customer,
    }


def createLineVisualization(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    output_file: Path,
    figsize: tuple[int, int] = Config.FIGSIZE_WIDE,
    color: str = Config.COLORS['sales_trend']
) -> None:
    """
    Create and save a line plot visualization.

    Args:
        data: DataFrame containing the data to plot.
        x_col: Column name for x-axis.
        y_col: Column name for y-axis.
        title: Title for the plot.
        output_file: Path to save the visualization.
        figsize: Figure size as (width, height) tuple.
        color: Color for the line.
    """
    try:
        plt.figure(figsize=figsize)
        plt.plot(data[x_col], data[y_col], linewidth=2, color=color)
        plt.title(title, fontsize=Config.FONT_SIZE_TITLE, fontweight="bold")
        plt.xlabel(x_col.capitalize())
        plt.ylabel(y_col.capitalize())
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_file, dpi=Config.DPI, bbox_inches=Config.BBOX_INCHES)
        plt.close()
        logger.info(f"Created {title}")
    except Exception as e:
        logger.error(f"Failed to create {title}: {e}")
        raise


def createBarVisualization(
    data: pd.Series,
    title: str,
    output_file: Path,
    kind: str = "bar",
    figsize: tuple[int, int] = Config.FIGSIZE_STANDARD,
    color: str = Config.COLORS['sales_by_store']
) -> None:
    """
    Create and save a bar plot visualization.

    Args:
        data: Series containing data to plot.
        title: Title for the plot.
        output_file: Path to save the visualization.
        kind: Type of plot ("bar" or "barh").
        figsize: Figure size as (width, height) tuple.
        color: Color for the bars.
    """
    try:
        plt.figure(figsize=figsize)
        data.plot(kind=kind, color=color)
        plt.title(title, fontsize=Config.FONT_SIZE_TITLE, fontweight="bold")
        if kind == "bar":
            plt.xlabel("Category")
            plt.xticks(rotation=45, ha="right")
        else:
            plt.xlabel("Amount")
        plt.ylabel("Amount" if kind == "bar" else "Category")
        plt.tight_layout()
        plt.savefig(output_file, dpi=Config.DPI, bbox_inches=Config.BBOX_INCHES)
        plt.close()
        logger.info(f"Created {title}")
    except Exception as e:
        logger.error(f"Failed to create {title}: {e}")
        raise


def createVisualizations(
    sales_data: pd.DataFrame,
    returns_data: pd.DataFrame,
    output_dir: Path
) -> None:
    """
    Create all visualization outputs.

    Args:
        sales_data: Merged sales data.
        returns_data: Merged returns data.
        output_dir: Directory to save visualizations.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Creating visualizations")

    sales_by_date = sales_data.groupby("date")["net_amount"].sum().reset_index()
    sales_by_date = sales_by_date.sort_values("date")
    createLineVisualization(
        sales_by_date,
        "date",
        "net_amount",
        "Sales Trend Over Time",
        output_dir / "sales_trend_over_time.png",
        color=Config.COLORS['sales_trend']
    )

    sales_by_store = sales_data.groupby("store_name")["net_amount"].sum().sort_values(ascending=False)
    createBarVisualization(
        sales_by_store,
        "Total Sales by Store",
        output_dir / "sales_by_store.png",
        kind="bar",
        color=Config.COLORS['sales_by_store']
    )

    sales_by_product = sales_data.groupby("product_name")["net_amount"].sum().sort_values(
        ascending=False
    ).head(Config.TOP_N_ITEMS)
    createBarVisualization(
        sales_by_product,
        f"Top {Config.TOP_N_ITEMS} Sales by Product",
        output_dir / "sales_by_product.png",
        kind="barh",
        color=Config.COLORS['sales_by_product']
    )

    sales_by_customer = sales_data.groupby("last_name")["net_amount"].sum().sort_values(
        ascending=False
    ).head(Config.TOP_N_ITEMS)
    createBarVisualization(
        sales_by_customer,
        f"Top {Config.TOP_N_ITEMS} Sales by Customer",
        output_dir / "sales_by_customer.png",
        kind="barh",
        color=Config.COLORS['sales_by_customer']
    )

    returns_by_date = returns_data.groupby("date")["refund_amount"].sum().reset_index()
    returns_by_date = returns_by_date.sort_values("date")
    createLineVisualization(
        returns_by_date,
        "date",
        "refund_amount",
        "Returns Trend Over Time",
        output_dir / "returns_trend_over_time.png",
        color=Config.COLORS['returns_trend']
    )

    returns_by_store = returns_data.groupby("store_name")["refund_amount"].sum().sort_values(
        ascending=False
    )
    createBarVisualization(
        returns_by_store,
        "Total Returns by Store",
        output_dir / "returns_by_store.png",
        kind="bar",
        color=Config.COLORS['returns_by_store']
    )

    returns_by_product = returns_data.groupby("product_name")["refund_amount"].sum().sort_values(
        ascending=False
    ).head(Config.TOP_N_ITEMS)
    createBarVisualization(
        returns_by_product,
        f"Top {Config.TOP_N_ITEMS} Returns by Product",
        output_dir / "returns_by_product.png",
        kind="barh",
        color=Config.COLORS['returns_by_product']
    )

    returns_by_customer = returns_data.groupby("last_name")["refund_amount"].sum().sort_values(
        ascending=False
    ).head(Config.TOP_N_ITEMS)
    createBarVisualization(
        returns_by_customer,
        f"Top {Config.TOP_N_ITEMS} Returns by Customer",
        output_dir / "returns_by_customer.png",
        kind="barh",
        color=Config.COLORS['returns_by_customer']
    )

    logger.info(f"All visualizations saved to {output_dir}")


def setupStyle() -> None:
    """Configure matplotlib and seaborn styling."""
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = Config.FIGSIZE_STANDARD
    plt.rcParams['font.size'] = Config.FONT_SIZE_DEFAULT


def main() -> None:
    """Main execution function."""
    try:
        data_dir = Path(os.getenv(
            "VISUALIZE_DATA_DIR",
            r"c:\ClaudeCode\.claude\skills\migrate\data\2026-06-05_08-35-07"
        ))
        output_dir = Path(os.getenv(
            "VISUALIZE_OUTPUT_DIR",
            r"c:\ClaudeCode\.claude\skills\visualize\visualizations"
        ))

        setupStyle()

        tables = loadDimensionTables(data_dir)

        sales_data = mergeSalesData(
            tables['fact_sales'],
            tables['dim_date'],
            tables['dim_store'],
            tables['dim_product'],
            tables['dim_customer']
        )

        returns_data = mergeReturnsData(
            tables['fact_returns'],
            tables['dim_date'],
            tables['dim_store'],
            tables['dim_product'],
            tables['fact_sales'],
            tables['dim_customer']
        )

        calculateKpis(
            tables['fact_sales'],
            tables['fact_returns'],
            sales_data,
            returns_data
        )

        createVisualizations(sales_data, returns_data, output_dir)

        logger.info("Visualization complete!")

    except Exception as e:
        logger.error(f"Error during visualization: {e}")
        raise


if __name__ == "__main__":
    main()
