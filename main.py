"""
This script reads a CSV file containing
data and creates a Word document for each row in the CSV file.
"""

import os
import sys
import pandas as pd
from tqdm import tqdm
from document_creator import create_doc_with_table, create_single_doc
from settings import ColumnSettings, ColumnType, DocumentSettings

RESULTS_FOLDER = "results"

sys.stdout.reconfigure(encoding="utf-8")

# Define the column that contains the unique identifier for each document
ID_COL = "num"

# Define the columns in the data
COLUMNS = [
    ColumnSettings("block/payment_phone.text1", "מספר טלפון", ColumnType.STRING),
    ColumnSettings("sign", "חתימה", ColumnType.IMAGE),
]

TITLE = "חתימת נבדק"  # Title of the document


# Create the results folder if it does not exist
if not os.path.exists(RESULTS_FOLDER):
    os.makedirs(RESULTS_FOLDER)

if __name__ == "__main__":
    FILE_NAME = "./payment.csv"  # The name of the CSV file

    # Load the data from the CSV file into a pandas DataFrame
    df = pd.read_csv(FILE_NAME)  # Load the data

    # Iterate over the rows in the DataFrame and create a document for each row
    for index, r in tqdm(df.iterrows(), total=df.shape[0]):
        create_single_doc(r, RESULTS_FOLDER, COLUMNS, DocumentSettings("num", TITLE))

    # Open the results folder in the file explorer
    os.startfile(RESULTS_FOLDER)

    create_doc_with_table(df, RESULTS_FOLDER, COLUMNS, DocumentSettings("num", TITLE))
