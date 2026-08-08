import pandas as pd
import sqlite3
import os

def assemble_analytics_panel():
    print("STATUS: Initiating SQL Feature Assembly...")
    
    # 1. Dynamically locate the root directory (Go up two levels from src/pipeline)
    pipeline_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(pipeline_dir))
    
    # Define the target directory and guarantee it exists
    data_dir = os.path.join(root_dir, 'data', 'processed')
    os.makedirs(data_dir, exist_ok=True)
    
    db_path = os.path.join(data_dir, 'risk_warehouse.db')
    export_path = os.path.join(data_dir, 'master_analytics_panel.csv')
    
    print(f"STATUS: Connecting to database at {db_path}...")
    
    try:
        conn = sqlite3.connect(db_path)
        
        # 2. The Advanced SQL CTE
        sql_query = """
        WITH loan_base AS (
            SELECT 
                p.reporting_date, 
                p.cohort_id, 
                p.npl_ratio,
                v.origination_date, 
                v.fico_tier, 
                v.interest_rate_type
            FROM portfolio_monthly_performance p
            JOIN internal_loan_vintages v ON p.cohort_id = v.cohort_id
        )
        SELECT 
            l.reporting_date,
            l.cohort_id,
            l.origination_date,
            l.fico_tier,
            l.interest_rate_type,
            l.npl_ratio,
            m.fdtr_index,
            m.usurtot_index AS unemployment_rate,
            m.cpi_yoy AS inflation_rate,
            m.ahe_yoy AS wage_growth
        FROM loan_base l
        LEFT JOIN macro_trends m ON l.reporting_date = m.observation_date
        ORDER BY l.cohort_id, l.reporting_date;
        """
        
        # 3. Pull directly into a Pandas DataFrame
        df_panel = pd.read_sql_query(sql_query, conn)
        
        # 4. Save back to the DB as a master view/table, and export to CSV
        df_panel.to_sql('master_analytics_panel', conn, if_exists='replace', index=False)
        df_panel.to_csv(export_path, index=False)
        
        print(f"STATUS: Assembly Complete. Master panel shape: {df_panel.shape}")
        print(f"STATUS: Saved flat CSV for modeling to: {os.path.abspath(export_path)}")
        
    except Exception as e:
        print(f"ERROR: SQL Assembly failed. Details: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    assemble_analytics_panel()