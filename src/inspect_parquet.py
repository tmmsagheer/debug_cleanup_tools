import pandas as pd
import sys
import os

def inspect_parquet_schema(file_path: str) -> None:
    """
    Executes a strict structural and statistical inspection of a target Parquet file.
    Designed to identify schema anomalies, hidden whitespace, and NaN propagations.
    """
    if not os.path.exists(file_path):
        print(f"CRITICAL: Target file not found at {file_path}")
        sys.exit(1)
        
    try:
        df = pd.read_parquet(file_path)
        
        print(f"\n{'='*60}")
        print(f"PARQUET INSPECTION REPORT: {os.path.basename(file_path)}")
        print(f"Dimensions: {df.shape[0]} rows x {df.shape[1]} columns")
        print(f"{'='*60}\n")
        
        print("1. RAW COLUMN SCHEMA (Bounds marked by quotes):")
        for col in df.columns:
            print(f"  -> '{col}' | Type: {df[col].dtype}")
            
        print("\n" + "-"*60 + "\n")
        
        print("2. NORMALIZED COLUMN MAPPING (Strip + Lower):")
        normalized_cols = df.columns.str.strip().str.lower()
        for raw, norm in zip(df.columns, normalized_cols):
            print(f"  -> Raw: '{raw}' -> Normalized: '{norm}'")
            
        print("\n" + "-"*60 + "\n")
        
        print("3. MISSING VALUE ANALYSIS (NaN/NaT):")
        null_counts = df.isnull().sum()
        missing_detected = False
        for col, count in null_counts.items():
            if count > 0:
                percentage = round((count / len(df)) * 100, 4)
                print(f"  -> '{col}': {count} missing values ({percentage}%)")
                missing_detected = True
                
        if not missing_detected:
            print("  -> ZERO missing values detected across all arrays.")
            
        print("\n" + "-"*60 + "\n")
        
        print("4. HEAD (Top 5 indices):")
        print(df.head(5).to_string())
        
        print("\n" + "-"*60 + "\n")
        
        print("5. TAIL (Bottom 5 indices):")
        print(df.tail(5).to_string())
        print(f"\n{'='*60}\n")
        
    except Exception as e:
        print(f"CRITICAL IO ERROR: Failed to parse Parquet structure. Trace: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Syntax Error. Usage: python3 inspect_parquet.py </path/to/file.parquet>")
        sys.exit(1)
        
    target = sys.argv[1]
    inspect_parquet_schema(target)