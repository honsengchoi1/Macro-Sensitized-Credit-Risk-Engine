import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import os

def run_did_regression():
    print("STATUS: Initiating DiD OLS Panel Regression...")

    # 1. Dynamically locate and load the CSV
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    csv_path = os.path.join(base_dir, 'data', 'processed', 'master_analytics_panel.csv')
    
    if not os.path.exists(csv_path):
        # Fallback for local terminal execution
        csv_path = 'data/processed/master_analytics_panel.csv'
        
    df = pd.read_csv(csv_path)
    
    # 2. Date Parsing & 2020 Burn-in Removal
    df['reporting_date'] = pd.to_datetime(df['reporting_date'])
    df = df.dropna(subset=['fdtr_index']).copy() # This drops 2020 where macro data is blank
    
    # 3. Engineer Dummy Variables (0/1 Indicators)
    # Time: 1 if on/after June 2022 (accounting for lag)
    shock_date = pd.to_datetime('2022-06-01')
    df['Time_PostShock'] = np.where(df['reporting_date'] >= shock_date, 1, 0)
    
    # Group: 1 if Variable Rate
    df['Group_Treated'] = np.where(df['interest_rate_type'] == 'Variable', 1, 0)
    
    # Interaction: The Causal Target
    df['Interaction_DiD'] = df['Time_PostShock'] * df['Group_Treated']
    
    # 4. Construct the OLS Regression Formula
    # npl_ratio is what we are predicting. Everything after the "~" are the predictors.
    formula = """
        npl_ratio ~ Group_Treated + Time_PostShock + Interaction_DiD + 
                    unemployment_rate + inflation_rate + wage_growth
    """
    
    # 5. Fit the Model and Print Results
    print("STATUS: Fitting OLS Model...")
    model = smf.ols(formula=formula, data=df).fit(cov_type='cluster', cov_kwds={'groups': df['cohort_id']})
    
    print("\n==============================================================================")
    print("                MACRO-SENSITIZED CREDIT DEFAULT MODEL (DiD)")
    print("==============================================================================")
    print(model.summary())
    print("==============================================================================\n")
    print("INTERPRETATION KEY:")
    print("-> Look at 'Interaction_DiD' (Beta 3). This is the true causal impact of the Fed Hike.")

if __name__ == "__main__":
    run_did_regression()