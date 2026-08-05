import pandas as pd
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Date, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# ---------------------------------------------------------
# 1. ENTERPRISE FILE PATHS
# ---------------------------------------------------------
# Assumes script is located in src/pipeline/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'econ_data.csv')
DB_DIR = os.path.join(BASE_DIR, 'data', 'processed')
DB_PATH = f"sqlite:///{os.path.join(DB_DIR, 'risk_warehouse.db')}"

# Ensure processed directory exists
os.makedirs(DB_DIR, exist_ok=True)

# ---------------------------------------------------------
# 2. ORM SCHEMA DEFINITION
# ---------------------------------------------------------
engine = create_engine(DB_PATH, echo=False)
Base = declarative_base()

class MacroTrend(Base):
    __tablename__ = 'macro_trends'
    observation_date = Column(Date, primary_key=True) 
    fdtr_index = Column(Float, nullable=False)    
    usurtot_index = Column(Float, nullable=False) 
    cpi_yoy = Column(Float, nullable=False)       
    ahe_yoy = Column(Float, nullable=False)       

# Build the blank schema if it doesn't exist
Base.metadata.create_all(engine)

# ---------------------------------------------------------
# 3. DEFENSIVE PARSING & ALIGNMENT LOGIC
# ---------------------------------------------------------
def normalize_dates(series):
    """Forces dates to 'YYYY-MM-01' to eliminate intraday/mid-month noise."""
    return pd.to_datetime(series).dt.to_period('M').dt.to_timestamp()

def build_database():
    print("STATUS: Initiating Defensive SQLite Warehouse Build...")

    try:
        raw_df = pd.read_csv(RAW_DATA_PATH)
        print(f"STATUS: Loaded raw CSV. Shape: {raw_df.shape}")
    except FileNotFoundError:
        print(f"CRITICAL ERROR: Could not find {RAW_DATA_PATH}.")
        return

    # 2. Extract and clean individual vectors
    try:
        # Extract FDTR
        fdtr = raw_df[['Date', 'FDTR Index']].dropna().copy()
        fdtr['Date'] = normalize_dates(fdtr['Date'])
        fdtr = fdtr.set_index('Date')[['FDTR Index']].rename(columns={'FDTR Index': 'fdtr_index'})

        # Extract USURTOT
        usur = raw_df[['Date.1', 'USURTOT Index']].dropna().copy()
        usur['Date'] = normalize_dates(usur['Date.1'])
        usur = usur.set_index('Date')[['USURTOT Index']].rename(columns={'USURTOT Index': 'usurtot_index'})

        # Extract CPI
        cpi = raw_df[['Date.2', 'CPI YOY Index']].dropna().copy()
        cpi['Date'] = normalize_dates(cpi['Date.2'])
        cpi = cpi.set_index('Date')[['CPI YOY Index']].rename(columns={'CPI YOY Index': 'cpi_yoy'})

        # Extract AHE
        ahe = raw_df[['Date.3', 'AHE YOY Index']].dropna().copy()
        ahe['Date'] = normalize_dates(ahe['Date.3'])
        ahe = ahe.set_index('Date')[['AHE YOY Index']].rename(columns={'AHE YOY Index': 'ahe_yoy'})

    except KeyError as e:
        print(f"CRITICAL ERROR: Missing expected column in CSV: {e}")
        print("Verify that pandas is suffixing duplicate Date headers as expected.")
        return

    # 3. The Fail-Safe Date Assertion (Symmetric Difference Check)
    dates_fdtr = set(fdtr.index)
    dates_usur = set(usur.index)
    dates_cpi = set(cpi.index)
    dates_ahe = set(ahe.index)

    if not (dates_fdtr == dates_usur == dates_cpi == dates_ahe):
        print("CRITICAL ERROR: PIPELINE ABORTED.")
        print("Timestamp discrepancy detected across macro streams. Vectors are not chronologically aligned.")
        return
    print("STATUS: Multi-vector date alignment verified. Proceeding to database commit.")

    # 4. Merge into a single master DataFrame
    master_df = fdtr.join([usur, cpi, ahe], how='inner').reset_index()

    # 5. Atomic Insertion via ORM
    Session = sessionmaker(bind=engine)
    with Session() as session:
        with session.begin():
            # Clear existing table data safely to prevent primary key collisions on rerun
            session.query(MacroTrend).delete()
            
            # Convert dataframe to list of dictionaries matching the ORM
            records = master_df.rename(columns={'Date': 'observation_date'}).to_dict(orient='records')
            
            # Bulk insert mapping directly to the SQLAlchemy models
            session.bulk_insert_mappings(MacroTrend, records)
            
    print("STATUS: Warehouse Build Complete. Atomic commit successful.")

if __name__ == "__main__":
    build_database()