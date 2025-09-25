"""
This module defines constants and enumerations used across the project.
It includes column definitions, document titles, image dimensions, and the results folder path.
"""

from collections import namedtuple
from enum import Enum

# Define a class to represent a column in the data
Column = namedtuple("Column", ["name", "display_name", "column_type"])

class ColumnType(Enum):
    """
    An enumeration of column types.
    """
    STRING = "string"
    IMAGE = "image"

# Define the column that contains the unique identifier for each document
ID_COL = "id"

# Define the columns in the data
COLUMNS = [
    Column("name", "שם", "string"),
    Column("amount", "סכום", "string"),
    Column("id", "תעודת זהות", "string"),
    Column("sign", "חתימה", "image"),
]

TITLE = "חתימת נבדק"  # Title of the document

# Define the size of the image to be inserted into the document
IMAGE_WIDTH = 4.0  # Inches
IMAGE_HEIGHT = 4.0  # Inches

# Define the folder where the results will be saved
RESULTS_FOLDER = "results"