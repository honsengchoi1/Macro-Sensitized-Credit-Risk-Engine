import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Set seed for reproducibility
np.random.seed(42)

# Timeline: 36 Months
months = np.arange(1, 37)

def generate_npl_series(base_npl, is_variable, add_noise=True):
    # 1. Base NPL (1.5% Prime, 4.5% Subprime)
    base = np.full(36, base_npl)
    
    # 2. Seasoning Curve (Sine wave peaking around month 18)
    seasoning = np.sin((months / 36) * np.pi) * 0.010 
    
    # 3. Macro Shock (2.5% step jump starting at Month 24 for Variable loans)
    shock = np.zeros(36)
    if is_variable:
        shock[23:] = 0.025  # Month 24 onwards (0-indexed 23)
        
    # 4. Stochastic White Noise
    noise = np.random.normal(0, 0.0015, 36) if add_noise else np.zeros(36)
    
    # Combined NPL
    npl = base + seasoning + shock + noise
    return np.maximum(0.001, npl) * 100  # Convert to Percentage

# Plotting setup
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharey=True)
fig.suptitle('Data Generating Process (DGP): Loan Default Trajectories over 36 Months', fontsize=16, fontweight='bold')

configs = [
    (0.015, False, 'Prime - Fixed Rate', axes[0, 0], 'green'),
    (0.015, True,  'Prime - Variable Rate (Fed Shock at M24)', axes[0, 1], 'blue'),
    (0.045, False, 'Subprime - Fixed Rate', axes[1, 0], 'orange'),
    (0.045, True,  'Subprime - Variable Rate (Fed Shock at M24)', axes[1, 1], 'red')
]

for base_npl, is_variable, title, ax, color in configs:
    npl_curve = generate_npl_series(base_npl, is_variable)
    ax.plot(months, npl_curve, marker='o', linewidth=2, color=color, label='Simulated NPL (%)')
    ax.axvline(x=24, color='black', linestyle='--', alpha=0.7, label='Fed Policy Shock (Month 24)')
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel('Loan Age (Months)')
    ax.set_ylabel('NPL Ratio (%)')
    ax.legend(loc='upper left')

plt.tight_layout()
plt.show()