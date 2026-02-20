# PavloviaSignReport

`PavloviaSignReport` generates Word documents from Pavlovia experiment results.

The project reads a CSV export file (e.g., from Pavlovia), extracts selected columns, and creates:

- A separate Word document for each participant
- A summary document containing a table of all entries

## Overview

The script:

1. Loads experiment results from a CSV file  
2. Extracts predefined columns (e.g., phone number, signature image)  
3. Generates individual `.docx` files  
4. Creates a combined report with a table  
5. Saves all files to a `results/` folder  

## Status

⚠️ **Work in progress**

- Configuration currently defined in `main.py`
- Assumes specific column names
- Not packaged as a CLI tool
- No validation layer yet

API and structure may change.

## Usage

1. Place your Pavlovia CSV file (e.g., `payment.csv`) in the project directory.
2. Adjust column definitions in `main.py` if needed.
3. Run:

```bash
python main.py
