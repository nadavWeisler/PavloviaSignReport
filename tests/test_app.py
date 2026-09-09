"""Tests for application workflow helpers."""

from pathlib import Path

import pandas as pd
import pytest
from docx import Document

from pavlovia_sign_report.app import (
    generate_reports,
    read_input_data,
    sanitize_filename,
    validate_dataframe,
)
from pavlovia_sign_report.models import ColumnSettings, ColumnType, DocumentSettings


def _columns() -> list[ColumnSettings]:
    return [
        ColumnSettings("name", "Name", ColumnType.STRING),
        ColumnSettings("amount", "Amount", ColumnType.NUMBER),
        ColumnSettings("completed", "Completed", ColumnType.BOOLEAN),
        ColumnSettings("sign", "Signature", ColumnType.IMAGE),
    ]


def _document_settings() -> DocumentSettings:
    return DocumentSettings(
        id_col="id",
        title="Report",
        summary_filename="summary-output.docx",
        output_filename_template="report-{safe_id}.docx",
        document_intro="Hello {name}",
        image_width=1,
        image_height=1,
        table_image_width=1,
        table_image_height=1,
    )


def test_sanitize_filename_replaces_invalid_characters():
    assert sanitize_filename("participant:/\\1") == "participant___1"


def test_read_input_data_rejects_empty_csv(tmp_path: Path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        read_input_data(str(path))


def test_validate_dataframe_rejects_duplicate_ids(sample_dataframe: pd.DataFrame):
    duplicated = sample_dataframe.copy()
    duplicated.loc[1, "id"] = duplicated.loc[0, "id"]

    with pytest.raises(ValueError, match="duplicate participant id"):
        validate_dataframe(duplicated, _columns(), _document_settings())


def test_validate_dataframe_rejects_missing_required_values(
    sample_dataframe: pd.DataFrame,
):
    invalid = sample_dataframe.copy()
    invalid.loc[0, "name"] = ""

    with pytest.raises(ValueError, match="required column 'name' is empty"):
        validate_dataframe(invalid, _columns(), _document_settings())


def test_validate_dataframe_rejects_invalid_image(sample_dataframe: pd.DataFrame):
    invalid = sample_dataframe.copy()
    invalid.loc[0, "sign"] = "data:image/png;base64,INVALID"

    with pytest.raises(ValueError, match="valid base64|supported image file"):
        validate_dataframe(invalid, _columns(), _document_settings())


def test_generate_reports_creates_documents(
    tmp_path: Path, sample_dataframe: pd.DataFrame
):
    summary = generate_reports(
        sample_dataframe,
        str(tmp_path),
        _columns(),
        _document_settings(),
    )

    assert summary.rows_processed == 2
    assert summary.summary_path == str(tmp_path / "summary-output.docx")
    assert (tmp_path / "report-participant_1.docx").exists()
    assert (tmp_path / "report-participant_2.docx").exists()
    assert (tmp_path / "summary-output.docx").exists()

    doc = Document(tmp_path / "report-participant_1.docx")
    assert any("Hello Alice" in paragraph.text for paragraph in doc.paragraphs)


def test_generate_reports_supports_dry_run(
    tmp_path: Path, sample_dataframe: pd.DataFrame
):
    summary = generate_reports(
        sample_dataframe,
        str(tmp_path),
        _columns(),
        _document_settings(),
        dry_run=True,
    )

    assert summary.summary_path is None
    assert not any(tmp_path.iterdir())
