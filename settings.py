"""A module to hold settings for the document and columns."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ColumnType(Enum):
    """An enumeration of column types."""

    STRING = "string"
    IMAGE = "image"


@dataclass
class DocumentSettings:
    """Holds document-level settings."""

    id_col: str
    title: str
    image_width: int = field(default=4)
    image_height: int = field(default=3)

@dataclass
class ColumnSettings:
    """Holds settings for a single column."""

    name: str
    display_name: Optional[str]
    column_type: ColumnType


__all__ = ["ColumnType", "DocumentSettings", "ColumnSettings"]
