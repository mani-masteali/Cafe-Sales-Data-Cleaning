import pandas as pd

def schema_normalization(df):
    # Create a copy of the DataFrame to avoid modifying the original data
    df = df.copy()
    # Normalize data types for each column
    df["Transaction ID"] = df["Transaction ID"].astype("string")
    df["Item"] = df["Item"].astype("string")
    df["Quantity"] = pd.to_numeric(df["Quantity"],errors="coerce").astype("Int64")  # Use nullable integer type
    df["Price Per Unit"] = pd.to_numeric(df["Price Per Unit"],errors="coerce") # Convert to numeric, coercing errors to NaN
    df["Total Spent"] = pd.to_numeric(df["Total Spent"],errors="coerce") # Convert to numeric, coercing errors to NaN
    df["Payment Method"] = df["Payment Method"].astype("string")
    df["Location"] = df["Location"].astype("string")
    df["Transaction Date"] = pd.to_datetime(df["Transaction Date"],errors="coerce") # Convert to datetime, coercing errors to NaT
    return df
df = pd.read_csv("dirty_cafe_sales.csv")
pd.set_option("display.max_columns",None)
df = schema_normalization(df)
# Display DataFrame info to verify schema normalization
print(df.info())