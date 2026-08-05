import pandas as pd
from sqlalchemy import create_engine
import os

# 1. Define File Paths (Enterprise Structure)
RAW_DATA_PATH = r"..\..\data\raw\econ_data.csv"
DB_PATH = r"sqlite:///..\..\data\processed\risk_warehouse.db"

def build_database():
    print("Initiating SQLite Warehouse Build...")

    # 2. Load the raw data
    try:
        df = pd.read_csv(RAW_DATA_PATH)
        print(f"Successfully loaded {len(df)} rows of macroeconomic data.")
    except FileNotFoundError:
        print("ERROR: Could not find econ_data.csv. Please ensure it is in the data/raw folder.")
        return

    # 3. Standardize the data (Convert 'Date' to datetime format for rolling math)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 4. Initialize SQLAlchemy Engine (The Forklift)
    engine = create_engine(DB_PATH)

    # 5. Push data to the SQLite Warehouse
    df.to_sql('macro_indicators', con=engine, if_exists='replace', index=False)
    
    print("Warehouse Build Complete: 'macro_indicators' table successfully created in risk_warehouse.db.")

if __name__ == "__main__":
    # Ensure the processed folder exists
    os.makedirs(r"..\..\data\processed", exist_ok=True)
    build_database()