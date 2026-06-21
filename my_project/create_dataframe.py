import pandas as pd

# Create a DataFrame with 3 columns and 5 rows
data = {
    'Column1': [1, 2, 3, 4, 5],
    'Column2': ['A', 'B', 'C', 'D', 'E'],
    'Column3': [10.5, 20.3, 30.1, 40.8, 50.2]
}

df = pd.DataFrame(data)

print("DataFrame created successfully:")
print(df)
print("\nDataFrame shape:", df.shape)
print("DataFrame info:")
print(df.info())