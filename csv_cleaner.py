import pandas as pd
import numpy as np

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
def sort_by_transaction_date(df):
    # Sort the DataFrame by Transaction Date in ascending order
    df = df.copy()
    df = df.sort_values(
    by=["Transaction Date", "Transaction ID"],
    kind="mergesort").reset_index(drop=True)
    return df
def validate_transaction_identity(df):
   # making sure whether transaction IDs are unique and not null
    df = df.copy()
    ID_COL = "Transaction ID"
    COLS = ["Transaction ID", "Item", "Quantity", "Price Per Unit", "Total Spent", "Payment Method", "Location", "Transaction Date"]
    id_is_null = df[ID_COL].isna()
    id_is_blank = df[ID_COL].fillna("").str.strip().eq("")
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
def reconstruct_monetary_fields(df):
    # Reconstruct Total Spent from Quantity and Price Per Unit
    df = df.copy()
    q = df["Quantity"]
    p = df["Price Per Unit"]
    t = df["Total Spent"]
    q_ok = q.notna()
    p_ok = p.notna()
    t_ok = t.notna()
    present_count = q_ok.astype(int) + p_ok.astype(int) + t_ok.astype(int)
    # Define flags based on the presence of monetary fields
    df["flag_money_complete"] = present_count == 3
    df["flag_money_reconstructable"] = (present_count == 2)
    df["flag_money_unrecoverable"] = present_count <= 1

    df["flag_need_total"] = (~t_ok) & q_ok & p_ok
    df["flag_need_quantity"] = (~q_ok) & p_ok & t_ok
    df["flag_need_price"] = (~p_ok) & q_ok & t_ok

    # division-by-zero blockers
    df["flag_div0_qty"] = df["flag_need_price"] & (q == 0)
    df["flag_div0_price"] = df["flag_need_quantity"] & (p == 0)

    df["flag_money_blocked"] = df["flag_div0_qty"] | df["flag_div0_price"]

    # Perform reconstruction where possible
    m_total = df["flag_need_total"]
    m_qty = df["flag_need_quantity"] & ~df["flag_div0_price"]
    m_price = df["flag_need_price"] & ~df["flag_div0_qty"]

    df["flag_reconstructed_total"] = m_total
    df["flag_reconstructed_quantity"] = m_qty
    df["flag_reconstructed_price"] = m_price

    df.loc[m_total, "Total Spent"] = df.loc[m_total, "Quantity"] * df.loc[m_total, "Price Per Unit"]
    qty_calc = df.loc[m_qty, "Total Spent"] / df.loc[m_qty, "Price Per Unit"]
    df.loc[m_qty, "Quantity"] = qty_calc.round().astype("Int64")  # Round to nearest integer and convert to nullable integer type
    df.loc[m_price, "Price Per Unit"] = df.loc[m_price, "Total Spent"] / df.loc[m_price, "Quantity"]

    q_ok2 = df["Quantity"].notna()
    p_ok2 = df["Price Per Unit"].notna()
    t_ok2 = df["Total Spent"].notna()
    present_count2 = q_ok2.astype(int) + p_ok2.astype(int) + t_ok2.astype(int)

    df["flag_money_complete"] = present_count2 == 3
    df["flag_money_reconstructable"] = (present_count2 == 2)
    df["flag_money_unrecoverable"] = present_count2 <= 1

    report = {
        "n_reconstructed_total": int(m_total.sum()),
        "n_reconstructed_quantity": int(m_qty.sum()),
        "n_reconstructed_price": int(m_price.sum()),
        "n_blocked_div0": int(df["flag_money_blocked"].sum()),
        "n_unrecoverable_after" : int(df["flag_money_unrecoverable"].sum()),
    }
    return df, report
def categorical_value_counts(df,col,dropna=True):
    # Get value counts for a categorical column, optionally including NaN values
    df = df.copy()
    return df[col].value_counts(dropna=dropna).to_dict()
def validate_money_consistency(df, tol=0.01):
    # Validate that Total Spent is approximately equal to Quantity * Price Per Unit within a specified tolerance
    df = df.copy()
    q = df["Quantity"]
    p = df["Price Per Unit"]
    t = df["Total Spent"]

    complete = q.notna() & p.notna() & t.notna()
    expected = q.astype(float) * p

    diff = (t - expected).abs()
    mismatch = complete & (diff > tol)
    
    df["flag_money_mismatch"] = mismatch
    df["money_expected_total"] = pd.Series(pd.NA, index=df.index, dtype="Float64")
    df.loc[complete, "money_expected_total"] = expected.loc[complete]

    report = {
        "n_checked_complete": int(complete.sum()),
        "n_money_mismatch": int(mismatch.sum()),
        "tol": float(tol),
    }
    return df, report
def build_quality_report(df):
    df = df.copy()
    issues = []
    id_col = "Transaction ID"
    # unrecovertable money issues
    if "flag_money_unrecoverable" in df.columns:
        m = df["flag_money_unrecoverable"].fillna(False)
        if m.any():
            issues.append(pd.DataFrame({ id_col: df.loc[m, id_col].astype("string").values, "issue": "unrecoverable_money"}))
    # missing dates
    m = df["Transaction Date"].isna()
    if m.any():
        issues.append(pd.DataFrame({ id_col: df.loc[m, id_col].astype("string").values, "issue": "missing_transaction_date"}))
    # money mismatches
    if "flag_money_mismatch" in df.columns:
        m = df["flag_money_mismatch"].fillna(False)
        if m.any():
            issues.append(pd.DataFrame({ id_col: df.loc[m, id_col].astype("string").values, "issue": "money_mismatch"}))
    if not issues:
        return pd.DataFrame(columns=[id_col, "issue"])
    report_df = pd.concat(issues, ignore_index=True)

    report_df = report_df.sort_values([id_col,"issue"]).reset_index(drop=True)
    return report_df


df = pd.read_csv("dirty_cafe_sales.csv")
pd.set_option("display.max_columns",None)
df = schema_normalization(df)
df = sort_by_transaction_date(df)
# Display DataFrame info to verify schema normalization
df.info()

df, id_report = validate_transaction_identity(df)
print("Transaction Identity Validation Report:", id_report)

df, money_report = reconstruct_monetary_fields(df)
print("Monetary Fields Reconstruction Report:", money_report)

print("null count (money):")
print(df[["Quantity", "Price Per Unit", "Total Spent"]].isna().sum())

item_counts = categorical_value_counts(df, "Item")
payment_counts = categorical_value_counts(df, "Payment Method")
location_counts = categorical_value_counts(df, "Location")
print("Item Value Counts:", item_counts)
print("Payment Method Value Counts:", payment_counts)
print("Location Value Counts:", location_counts)