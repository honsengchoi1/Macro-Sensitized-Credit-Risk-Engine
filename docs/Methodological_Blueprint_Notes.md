# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 16:16:16 2026

@author: hon19
"""

# ==============================================================================
# METHODOLOGICAL NOTE: EXPERIMENTAL DESIGN & COUNTERFACTUAL LOGIC
# ==============================================================================
# Traditional A/B testing relies on active randomization to isolate causal effects.
# In systemic credit risk, active randomization of interest rates is prohibited by
# adverse selection, risk-based pricing rules, and compliance frameworks.
#
# This pipeline implements a Natural Experiment via Difference-in-Differences (DiD).
# It utilizes the exact same 'Counterfactual' logic as an A/B test by exploiting 
# an exogenous market shock (+525bps Fed tightening) to isolate causal portfolio decay,
# comparing a Variable-Rate treatment group against a Fixed-Rate control baseline.
# ==============================================================================
