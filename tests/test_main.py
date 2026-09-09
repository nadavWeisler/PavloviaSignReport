"""Tests for config loading and CLI helpers."""

import json
from pathlib import Path

import pytest

from main import load_columns_from_config, parse_args
from pavlovia_sign_report.cli import build_document_settings, open_folder
from pavlovia_sign_report.config import load_config
from pavlovia_sign_report.models import ColumnType, ReportConfig


def test_load_columns_from_legacy_config(tmp_path: Path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            [
                {"name": "name", "display_name": "Name", "type": "string"},
                {"name": "sign", "display_name": "Signature", "type": "image"},
            ]
        ),
        encoding="utf-8",
    )

    columns = load_columns_from_config(str(config_path))

    assert [column.column_type for column in columns] == [
        ColumnType.STRING,
        ColumnType.IMAGE,
    ]


def test_load_config_supports_document_section(tmp_path: Path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "document": {"summary_filename": "custom-summary.docx"},
                "columns": [{"name": "completed", "type": "boolean"}],
            }
        ),
        encoding="utf-8",
    )

    config = load_config(str(config_path))

    assert config.document["summary_filename"] == "custom-summary.docx"
    assert config.columns[0].column_type == ColumnType.BOOLEAN


def test_load_config_rejects_unknown_document_option(tmp_path: Path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"document": {"unknown": True}, "columns": []}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unsupported document option"):
        load_config(str(config_path))


def test_open_folder_raises_on_non_directory(tmp_path: Path):
    with pytest.raises(ValueError, match="not an existing directory"):
        open_folder(str(tmp_path / "missing"))


def test_parse_args_supports_new_options():
    args = parse_args(
        [
            "--file",
            "data.csv",
            "--summary-filename",
            "summary.docx",
            "--output-template",
            "report-{safe_id}.docx",
            "--document-intro",
            "Hello {name}",
            "--dry-run",
        ]
    )

    assert args.file == "data.csv"
    assert args.summary_filename == "summary.docx"
    assert args.output_template == "report-{safe_id}.docx"
    assert args.document_intro == "Hello {name}"
    assert args.dry_run is True


def test_build_document_settings_merges_defaults_and_config():
    args = parse_args(["--title", "CLI Title", "--image-width", "1.5"])
    config = ReportConfig(columns=[], document={"summary_filename": "from-config.docx"})

    settings = build_document_settings(args, config)

    assert settings.title == "CLI Title"
    assert settings.summary_filename == "from-config.docx"
    assert settings.image_width == 1.5
