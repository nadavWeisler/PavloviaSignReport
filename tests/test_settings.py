"""Tests for report settings models."""

from pavlovia_sign_report.models import (
    ColumnSettings,
    ColumnType,
    DocumentSettings,
    ReportConfig,
)


def test_column_type_members():
    assert {member.value for member in ColumnType} == {
        "string",
        "image",
        "number",
        "boolean",
    }


def test_column_settings_defaults():
    column = ColumnSettings("completed", "Completed", ColumnType.BOOLEAN)

    assert column.required is True
    assert column.true_text == "Yes"
    assert column.false_text == "No"


def test_document_settings_defaults():
    settings = DocumentSettings(id_col="id", title="Report")

    assert settings.summary_filename == "summary.docx"
    assert settings.output_filename_template == "{safe_id}.docx"
    assert settings.document_intro is None


def test_report_config_defaults():
    config = ReportConfig(columns=[])
    assert config.document == {}
