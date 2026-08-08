import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ks_2samp
import sqlite3
import os
import warnings
warnings.filterwarnings('ignore')

def run_ks_test():
    print("STATUS: Initiating K-S Test EDA for Variable Rate Loans...")

    # 1. Dynamically locate the Database
    # Assuming your script is in src/pipeline/ and DB is in data/processed/
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, 'data', 'processed', 'risk_warehouse.db')
    
    # Fallback if the strict path above fails (checks the current running directory)
    if not os.path.exists(db_path):
        db_path = 'risk_warehouse.db'
        
    print(f"STATUS: Connecting to database at {db_path}...")

    try:
        conn = sqlite3.connect(db_path)
        
        # 2. The SQL Query (This creates the relationship dynamically!)
        # We push the filtering (Variable loans, > 2021) directly to the SQL engine for maximum efficiency.
        sql_query = """
        SELECT 
            p.reporting_date, 
            p.npl_ratio
        FROM 
            portfolio_monthly_performance p
        INNER JOIN 
            internal_loan_vintages v ON p.cohort_id = v.cohort_id
        WHERE 
            v.interest_rate_type = 'Variable' 
            AND p.reporting_date >= '2021-01-01';
        """
        
        df_var = pd.read_sql_query(sql_query, conn)
        conn.close()
        print("STATUS: Data successfully extracted from risk_warehouse.db.")
        
    except Exception as e:
        print(f"ERROR: Database connection failed. Details: {e}")
        return

    # Ensure dates are datetime objects
    df_var['reporting_date'] = pd.to_datetime(df_var['reporting_date'])

    # 3. Split the data into Pre-Shock and Post-Shock
    # Shock date is June 2022 (Accounting for the 3-month lag from the March 2022 hike)
    shock_date = pd.to_datetime('2022-06-01')
    
    pre_shock = df_var[df_var['reporting_date'] < shock_date]['npl_ratio']
    post_shock = df_var[df_var['reporting_date'] >= shock_date]['npl_ratio']

    # 4. Execute the Kolmogorov-Smirnov (K-S) Test
    ks_stat, p_value = ks_2samp(pre_shock, post_shock)
    
    print(f"\n--- K-S TEST RESULTS ---")
    print(f"Pre-Shock Observations (N):  {len(pre_shock)}")
    print(f"Post-Shock Observations (N): {len(post_shock)}")
    print(f"K-S Statistic:               {ks_stat:.4f}")
    print(f"P-Value:                     {p_value:.4e}")
    
    if p_value < 0.05:
        print("CONCLUSION: Statistically significant distribution shift detected (Reject Null).")
    else:
        print("CONCLUSION: No significant shift detected (Fail to reject Null).")

    # 5. Generate the Executive Visual (Density Plot)
    plt.figure(figsize=(10, 6))
    sns.kdeplot(pre_shock, fill=True, color='blue', label='Pre-Shock (2021 - May 2022)', alpha=0.5)
    sns.kdeplot(post_shock, fill=True, color='red', label='Post-Shock (June 2022 - Dec 2023)', alpha=0.5)
    
    plt.title('Variable Loan Default Distributions: Pre vs. Post Fed Shock', fontsize=14, fontweight='bold')
    plt.xlabel('Non-Performing Loan (NPL) Ratio', fontsize=12)
    plt.ylabel('Density', fontsize=12)
    plt.axvline(pre_shock.mean(), color='blue', linestyle='--', alpha=0.7, label='Pre-Shock Mean')
    plt.axvline(post_shock.mean(), color='red', linestyle='--', alpha=0.7, label='Post-Shock Mean')
    
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('ks_test_distribution_shift.png', dpi=300)
    print("\nSTATUS: Visual saved as 'ks_test_distribution_shift.png'")
    plt.show()

if __name__ == "__main__":
    run_ks_test()