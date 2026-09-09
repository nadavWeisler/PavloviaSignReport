"""Core data models for PavloviaSignReport."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ColumnType(Enum):
    """Supported column types in the report configuration."""

    STRING = "string"
    IMAGE = "image"
    NUMBER = "number"
    BOOLEAN = "boolean"


@dataclass(slots=True)
class DocumentSettings:
    """Document-level settings controlling output generation."""

    id_col: str
    title: str
    image_width: float = field(default=4.0)
    image_height: float = field(default=3.0)
    table_image_width: float = field(default=2.0)
    table_image_height: float = field(default=2.0)
    summary_filename: str = field(default="summary.docx")
    output_filename_template: str = field(default="{safe_id}.docx")
    document_intro: str | None = field(default=None)


@dataclass(slots=True)
class ColumnSettings:
    """Settings for a single configured output column."""

    name: str
    display_name: str | None
    column_type: ColumnType
    required: bool = True
    true_text: str = "Yes"
    false_text: str = "No"


@dataclass(slots=True)
class ReportConfig:
    """Parsed configuration file contents."""

    columns: list[ColumnSettings]
    document: dict[str, object] = field(default_factory=dict)


__all__ = ["ColumnType", "ColumnSettings", "DocumentSettings", "ReportConfig"]
