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
def validate_transaction_identity(df):
   # making sure whether transaction IDs are unique and not null
    df = df.copy()
    ID_COL = "Transaction ID"
    COLS = ["Transaction ID", "Item", "Quantity", "Price Per Unit", "Total Spent", "Payment Method", "Location", "Transaction Date"]
    id_is_null = df[ID_COL].isna()
    id_is_blank = df[ID_COL].filna("").str.strip().eq("")
    id_missing = id_is_null | id_is_blank
    id_present = ~id_missing
    id_duplicated = id_present & df[ID_COL].duplicated(keep=False)
    row_exact_duo = df.duplicated(subset=COLS, keep=False)
    df["flag_id_missing"] = id_missing
    df["flag_id_duplicated"] = id_duplicated
    df["flag_row_exact_duo"] = row_exact_duo
    report = {
        "n_rows": int(len(df)),
        "n_id_missing": int(id_missing.sum()),
        "n_id_duplicated_rows": int(id_duplicated.sum()),
        "n_id_duplicated_unique" : int(df.loc[id_duplicated, ID_COL].nunique()),
        "n_exact_duplicated_rows" : int(row_exact_duo.sum()),
    }
    return df, report

df = pd.read_csv("dirty_cafe_sales.csv")
pd.set_option("display.max_columns",None)
df = schema_normalization(df)
# Display DataFrame info to verify schema normalization
print(df.info())