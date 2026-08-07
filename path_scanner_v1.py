# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 06:50:52 2026

@author: hsc
"""

import os

# Get your current working folder
working_dir = os.getcwd()

print("```text")
print(f"Project Root Folder: {working_dir}\n")

for root, dirs, files in os.walk(working_dir):
    # Hide noisy system folders so the output stays very clean
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
    
    # Calculate how deep the current folder is
    level = root.replace(working_dir, '').count(os.sep)
    indent = '    ' * level
    
    # Print the folder name
    print(f"{indent}[Folder] {os.path.basename(root)}")
    
    # Print the files inside that folder
    subindent = '    ' * (level + 1)
    for f in files:
        if not f.startswith('.'):
            print(f"{subindent}- {f}")
print("```")
