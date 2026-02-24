# debug_cleanup_tools

A repository of lightweight, standalone Python utility scripts designed for data debugging, structural inspection, and workflow cleanup. These tools are built to help quickly identify schema anomalies, hidden data quality issues, and structural inconsistencies in various datasets.

## 📦 Prerequisites

Most scripts in this repository utilize standard data science libraries. To ensure full compatibility, make sure you have the following installed:

* Python 3.7+
* `pandas`
* A Parquet engine (e.g., `pyarrow` or `fastparquet`)

You can install the base dependencies via pip:

```bash
pip install pandas pyarrow
```
## 🛠️ Available Tools
### 1. inspect_parquet.py

Executes a strict structural and statistical inspection of a target Parquet file. It is specifically designed to expose hidden whitespaces in column names, identify schema anomalies, and track NaN/NaT propagations.

#### Features:

- Raw Column Schema: Outputs exact column names enclosed in quotes to reveal trailing/leading whitespaces.

- Normalized Column Mapping: Previews how column names look when stripped of whitespace and converted to lowercase.

- Missing Value Analysis: Calculates precise missing value counts and percentages across all columns.

- Data Preview: Outputs a clean string representation of the head (top 5) and tail (bottom 5) records.

#### Usage:
```Bash

python3 inspect_parquet.py </path/to/file.parquet>
```
**Example Output:**
```Plaintext

============================================================
PARQUET INSPECTION REPORT: SBIN_20200225_20251230_1m.parquet
Dimensions: 541395 rows x 6 columns
============================================================

1. RAW COLUMN SCHEMA (Bounds marked by quotes):
  -> 'Open' | Type: float64
  -> 'High' | Type: float64
  -> 'Low' | Type: float64
  -> 'Close' | Type: float64
  -> 'Volume' | Type: float64
  -> 'Datetime' | Type: object

------------------------------------------------------------

2. NORMALIZED COLUMN MAPPING (Strip + Lower):
  -> Raw: 'Open' -> Normalized: 'open'
  -> Raw: 'High' -> Normalized: 'high'
  -> Raw: 'Low' -> Normalized: 'low'
  -> Raw: 'Close' -> Normalized: 'close'
  -> Raw: 'Volume' -> Normalized: 'volume'
  -> Raw: 'Datetime' -> Normalized: 'datetime'

------------------------------------------------------------

3. MISSING VALUE ANALYSIS (NaN/NaT):
  -> ZERO missing values detected across all arrays.

------------------------------------------------------------

4. HEAD (Top 3 indices):
                            Open   High     Low   Close    Volume             Datetime
2020-02-25 09:15:00+05:30  325.9  325.9  324.40  325.00  592059.0  2020-02-25 09:15:00
2020-02-25 09:16:00+05:30  325.1  325.2  324.25  324.45  297302.0  2020-02-25 09:16:00
2020-02-25 09:17:00+05:30  324.3  324.8  324.15  324.60  279199.0  2020-02-25 09:17:00

------------------------------------------------------------

5. TAIL (Bottom 5 indices):
                             Open    High     Low   Close    Volume             Datetime
2025-12-30 15:25:00+05:30  973.55  973.65  971.95  972.45  222871.0  2025-12-30 15:25:00
2025-12-30 15:26:00+05:30  972.50  973.20  972.30  972.95  193580.0  2025-12-30 15:26:00
2025-12-30 15:27:00+05:30  972.60  973.25  972.15  972.30  182040.0  2025-12-30 15:27:00
2025-12-30 15:28:00+05:30  972.30  972.90  971.60  972.90   90817.0  2025-12-30 15:28:00
2025-12-30 15:29:00+05:30  972.90  974.00  972.05  973.10   28553.0  2025-12-30 15:29:00

============================================================
```
