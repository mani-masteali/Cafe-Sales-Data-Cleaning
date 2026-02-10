<h1>Cafe Sales Data Cleaning Project</h1>

<h2>Overview</h2>
This project focuses on cleaning and validating a cafe sales dataset containing 10,000 transaction records. The goal was not to aggressively modify the data, but to make it analysis-ready while preserving business context and data integrity. Wherever information could not be safely recovered, it was reported instead of guessed or fabricated.

<h2>Dataset</h2>
-   Rows: 10,000
-   Source: https://www.kaggle.com/datasets/ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training/data
- Structure: Transaction-level sales records
- Goal: Clean and validate the data without altering meaning of transactions.

<h2>Cleaning Steps</h2>
<h3>1. Schema Normalization</h3>
All columns were explicitly cast to appropriate data types (strings, nullable integers, floats, and datetimes).
Invalid values such as "ERROR" or "UNKNOWN" in numeric and date columns were coerced into missing values.
<h4>Why:</h4>
Real-world datasets often contain mixed or incorrect types. Normalizing a schema is a prerequisite for reliable validation and calculations.
<h3>2.Transaction Identity Validation</h3>
Each Transaction was checked to ensure:
- Transaction IDs are present
- Transaction IDs are unique
- No fully duplicated rows exist
<h4>Result:</h4>
No missing IDs, no duplicate IDs, and no exact duplicate rows were found.
<h4>Why:</h4>
Transaction IDs are assumed to uniquely identify sales. Any ambiguity here would invalidate downstream analysis.
<h3>3. Monetary Reconstruction</h3>
The three monetary fields(Quantity, Price Per Unit, Total Spent) were evaluated row by row.
Logic applied:
- If exactly one monetary value was missing and the other two were present, the missing value was reconstructed.
- Division-by-zero cases were explicitly blocked
- Rows missing two or more monetary values were marked as unrecoverable
<h4>Results:</h4>
- Total Spent reconstructed: 462 rows
- Quantity reconstructed : 441 rows
- Price Per Unit reconstructed: 495 rows
- Unrecoverable monetary rows: 58
<h4>Why:</h4>
Monetary fields have deterministic relationships. Reconstruction was applied only when it was mathematically and logically safe.
<h3>Consistency Checks</h3>
For all rows where Quantity, Price Per Unit, and Total Spent were present, the following was validated:
Quantity × Price Per Unit ≈ Total Spent
Using a tolerance of ±0.01:
- Rows Checked: 9,942
- Mismatches found: 0
<h4>Why:</h4>
This ensures both original and reconstructed values are suitable for analysis.

<h2>Data Quality Report</h2>
Unresolved issues were exported to a seperate file (data_quality_issues.csv) instead of being fixed automatically.
Reported issues:
- Missing transaction dates: 460 rows
- Unrecoverable monetary data: 58 rows
Each issue is listed by transaction ID.
<h3>Why not auto-fix?</h3>
Filling missing dates, locations or payment methods without business rules would introduce fabricated data. Reporting these rows preserves transparency and allows stakeholders to decide how to handle them.

<h2>Final Outputs</h2>
- clean_cafe_sales.csv : cleaned, schema-stable dataset ready for analysis
- data_quality_issues.csv: audit-friendly list of unresolved data quality issues

<h2>Notes</h2>
The following actions were intentionally not taken:
- No dates were inferred or fabricated
- No locations or payment methods were guessed
- No rows were dropped solely due to missing non-critical fields
- No categorical values were inferred from prices
The emphasis of this project is correctness, transparency, and auditability rather than aggressive data modification.

<h2> Tools & Stack </h2>
- Python (pandas, numpy)
- CSV-based pipeline
- Deterministic rule-based validation (no ML inference)