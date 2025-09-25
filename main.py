"""
This script reads a CSV file containing
data and creates a Word document for each row in the CSV file.
"""

import os
from collections import namedtuple
import pandas as pd
from tqdm import tqdm
from document_creator import create_doc_with_table, create_doc
from constants import RESULTS_FOLDER
import sys

sys.stdout.reconfigure(encoding="utf-8")
# Define a class to represent a column in the data

Column = namedtuple("Column", ["name", "display_name", "column_type"])


class ColumnType:
    """
    An enumeration of column types.
    """

    STRING = "string"
    IMAGE = "image"


# Define the column that contains the unique identifier for each document
ID_COL = "num"

# Define the columns in the data
COLUMNS = [
    Column("block/payment_phone.text1", "שם", "string"),
    # Column("id", "string"),
    # Column("סכום", "סכום", "string"),
    # Column("responseDate", "תאריך", "string"),
    Column("sign", "חתימה", "image"),
]

TITLE = "חתימת נבדק"  # Title of the document

# Define the size of the image to be inserted into the document
IMAGE_WIDTH = 4.0  # Inches
IMAGE_HEIGHT = 4.0  # Inches

# Create the results folder if it does not exist
if not os.path.exists(RESULTS_FOLDER):
    os.makedirs(RESULTS_FOLDER)

if __name__ == "__main__":
    FILE_NAME = "./file.csv"  # The name of the CSV file

    # Load the data from the CSV file into a pandas DataFrame
    df = pd.read_csv(FILE_NAME)  # Load the data
    print(df.columns)
    # Iterate over the rows in the DataFrame and create a document for each row
    for index, r in tqdm(df.iterrows(), total=df.shape[0]):
        create_doc(r, RESULTS_FOLDER)

    # Open the results folder in the file explorer
    os.startfile(RESULTS_FOLDER)

    create_doc_with_table(df, RESULTS_FOLDER)
