import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import os

# 1. Set seed for reproducible portfolio generation
np.random.seed(42)

def generate_synthetic_portfolio():
    print("STATUS: Initiating Synthetic Loan Portfolio Generation...")
    
    # 2. Define Timeline
    start_date = pd.to_datetime('2020-01-01')
    end_date = pd.to_datetime('2023-12-01')
    months = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    # 3. Generate Table A: Loan Vintages (Static Origination Data)
    cohorts = []
    # Originations stop 12 months before end date to allow seasoning
    for date in months[:-12]: 
        for fico in ['Prime', 'Subprime']:
            for rate_type in ['Fixed', 'Variable']:
                cohorts.append({
                    'cohort_id': f"C_{date.strftime('%Y%m')}_{fico[0]}_{rate_type[0]}",
                    'origination_date': date.strftime('%Y-%m-%d'),
                    'fico_tier': fico,
                    'interest_rate_type': rate_type
                })
    
    df_vintages = pd.DataFrame(cohorts)
    print(f"STATUS: Generated {len(df_vintages)} unique loan cohorts.")

    # 4. Generate Table B: Monthly Performance (The Natural Experiment DGP)
    performance = []
    fed_hike_effective_date = pd.to_datetime('2022-06-01') # March 2022 + 3 month transmission lag
    
    for _, cohort in df_vintages.iterrows():
        orig_date = pd.to_datetime(cohort['origination_date'])
        
        # Portfolio ages over time (max 36 months for this simulation)
        active_months = [m for m in months if m > orig_date][:36] 
        
        for current_date in active_months:
            # Baseline NPL derived from FICO Spread
            base_npl = 0.015 if cohort['fico_tier'] == 'Prime' else 0.045
            
            # Natural seasoning curve (defaults organically peak midway through lifecycle)
            age_months = (current_date.year - orig_date.year) * 12 + (current_date.month - orig_date.month)
            seasoning_factor = np.sin((age_months / 36) * np.pi) * 0.01 
            
            # THE SHOCK: The DiD Target for Variable Rate Loans
            rate_shock = 0.0
            if current_date >= fed_hike_effective_date and cohort['interest_rate_type'] == 'Variable':
                multiplier = 1.8 if cohort['fico_tier'] == 'Subprime' else 1.2
                rate_shock = 0.025 * multiplier 
                
            # Add stochastic white noise to simulate real reporting variance
            noise = np.random.normal(0, 0.002)
            
            # Final NPL Calculation (Floor at 0.1% to prevent negative defaults)
            npl_ratio = max(0.001, base_npl + seasoning_factor + rate_shock + noise)
            
            performance.append({
                'reporting_date': current_date.strftime('%Y-%m-%d'),
                'cohort_id': cohort['cohort_id'],
                'npl_ratio': round(npl_ratio, 4)
            })

    df_performance = pd.DataFrame(performance)
    print(f"STATUS: Generated {len(df_performance)} monthly performance records.")
    
    return df_vintages, df_performance

def commit_to_warehouse(df_vintages, df_performance):
    """Commits the synthetic dataframes directly into the SQLite warehouse."""
    # Robust path resolution to find the DB regardless of where terminal is opened
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, '../data/processed/risk_warehouse.db')
    
    print(f"STATUS: Connecting to Data Warehouse at {os.path.abspath(db_path)}...")
    
    try:
        conn = sqlite3.connect(db_path)
        
        # =====================================================================
        #TECH DEBT NOTE:
        # Using `if_exists='replace'` executes a DROP TABLE command, which 
        # destroys Primary/Foreign Key constraints. This is acceptable here 
        # for clean local synthetic generation runs.
        #
        # IN PRODUCTION: We would explicitly define the SQLAlchemy ORM schema 
        # and use an UPSERT (Insert/Update) operation to protect historical 
        # data and maintain referential integrity.
        # =====================================================================
        df_vintages.to_sql('internal_loan_vintages', conn, if_exists='replace', index=False)
        df_performance.to_sql('portfolio_monthly_performance', conn, if_exists='replace', index=False)
        
        conn.commit()
        print("STATUS: Milestone 2 Complete. Synthetic credit data successfully injected into warehouse.")
    except Exception as e:
        print(f"ERROR: Database connection failed. Details: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    vintages, performance = generate_synthetic_portfolio()
    commit_to_warehouse(vintages, performance)