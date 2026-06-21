"""Utility module for creating sample Pandas dataframes."""

import pandas as pd


def create_sample_dataframe() -> pd.DataFrame:
    """Create a sample Pandas dataframe with 3 columns and 5 rows.

    Returns:
        pd.DataFrame: A dataframe with columns 'Name', 'Age', and 'Score',
                     populated with 5 rows of sample data.
    """
    data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'Age': [25, 30, 35, 28, 32],
        'Score': [85.5, 90.2, 78.9, 88.4, 92.1]
    }
    return pd.DataFrame(data)


if __name__ == '__main__':
    df = create_sample_dataframe()
    print(df)
