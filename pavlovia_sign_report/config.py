"""Configuration loading and validation helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pavlovia_sign_report.models import ColumnSettings, ColumnType, ReportConfig

DEFAULT_FILE = "./examples/input/payment.csv"
DEFAULT_ID_COL = "num"
DEFAULT_TITLE = "חתימת נבדק"
DEFAULT_RESULTS_FOLDER = "results"
DEFAULT_COLUMNS = [
    ColumnSettings("block/payment_phone.text1", "מספר טלפון", ColumnType.STRING),
    ColumnSettings("sign", "חתימה", ColumnType.IMAGE),
]

_DOCUMENT_OPTION_TYPES: dict[str, type[Any] | tuple[type[Any], ...]] = {
    "title": str,
    "image_width": (int, float),
    "image_height": (int, float),
    "table_image_width": (int, float),
    "table_image_height": (int, float),
    "summary_filename": str,
    "output_filename_template": str,
    "document_intro": str,
}


def load_columns_from_config(config_path: str) -> list[ColumnSettings]:
    """Backwards-compatible helper for legacy callers."""

    return load_config(config_path).columns


def load_config(config_path: str) -> ReportConfig:
    """Load a report config from JSON.

    Supported formats:
    - legacy: a JSON array of column objects
    - current: an object with "columns" and optional "document" sections
    """

    path = Path(config_path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Config file '{config_path}' does not exist.") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Config file '{config_path}' is not valid JSON: {exc.msg}."
        ) from exc

    if isinstance(raw, list):
        return ReportConfig(columns=_parse_columns(raw, config_path))

    if not isinstance(raw, dict):
        raise ValueError(
            f"Config file '{config_path}' must contain either a JSON array "
            "or an object, "
            f"got {type(raw).__name__}."
        )

    allowed_top_level = {"columns", "document"}
    unknown_top_level = sorted(set(raw) - allowed_top_level)
    if unknown_top_level:
        raise ValueError(
            f"Config file '{config_path}' contains unsupported top-level keys: "
            f"{unknown_top_level}. Supported keys are ['columns', 'document']."
        )

    columns = raw.get("columns")
    if columns is None:
        raise ValueError(
            f"Config file '{config_path}' must include a 'columns' array "
            "when using the object format."
        )

    document = raw.get("document", {})
    if not isinstance(document, dict):
        raise ValueError(
            f"The 'document' section in '{config_path}' must be an object, "
            f"got {type(document).__name__}."
        )

    return ReportConfig(
        columns=_parse_columns(columns, config_path),
        document=_parse_document_settings(document, config_path),
    )


def _parse_columns(entries: Any, config_path: str) -> list[ColumnSettings]:
    if not isinstance(entries, list):
        raise ValueError(
            f"Config file '{config_path}' must contain a JSON array of column objects, "
            f"got {type(entries).__name__}."
        )

    type_map = {column_type.value: column_type for column_type in ColumnType}
    columns: list[ColumnSettings] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(
                f"Entry {index} in config '{config_path}' must be an object, "
                f"got {type(entry).__name__}."
            )

        for required_key in ("name", "type"):
            if required_key not in entry:
                raise ValueError(
                    f"Entry {index} in config '{config_path}' is missing "
                    f"required key '{required_key}'."
                )

        name = entry["name"]
        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"Entry {index} in config '{config_path}' has an invalid "
                "'name'. It must be a non-empty string."
            )

        raw_type = str(entry["type"]).lower()
        column_type = type_map.get(raw_type)
        if column_type is None:
            raise ValueError(
                f"Entry {index} in config '{config_path}' has unknown type "
                f"'{entry['type']}'. "
                f"Valid types: {sorted(type_map)}."
            )

        required = entry.get("required", True)
        if not isinstance(required, bool):
            raise ValueError(
                f"Entry {index} in config '{config_path}' has an invalid "
                "'required' value. "
                "It must be true or false."
            )

        display_name = entry.get("display_name", name)
        if display_name is not None and not isinstance(display_name, str):
            raise ValueError(
                f"Entry {index} in config '{config_path}' has an invalid "
                "'display_name'. "
                "It must be a string when provided."
            )

        true_text = entry.get("true_text", "Yes")
        false_text = entry.get("false_text", "No")
        if column_type == ColumnType.BOOLEAN:
            if not isinstance(true_text, str) or not isinstance(false_text, str):
                raise ValueError(
                    f"Entry {index} in config '{config_path}' must define "
                    "'true_text' and 'false_text' as strings."
                )
        elif "true_text" in entry or "false_text" in entry:
            raise ValueError(
                f"Entry {index} in config '{config_path}' can only use "
                "'true_text' and 'false_text' with boolean columns."
            )

        columns.append(
            ColumnSettings(
                name=name,
                display_name=display_name,
                column_type=column_type,
                required=required,
                true_text=true_text,
                false_text=false_text,
            )
        )

    return columns


def _parse_document_settings(
    document: dict[str, Any], config_path: str
) -> dict[str, object]:
    parsed: dict[str, object] = {}
    for key, value in document.items():
        expected_type = _DOCUMENT_OPTION_TYPES.get(key)
        if expected_type is None:
            raise ValueError(
                f"Config file '{config_path}' contains an unsupported "
                f"document option '{key}'."
            )

        if not isinstance(value, expected_type):
            raise ValueError(
                f"Document option '{key}' in '{config_path}' has the wrong type."
            )

        if isinstance(value, str) and not value.strip():
            raise ValueError(
                f"Document option '{key}' in '{config_path}' must not be empty."
            )

        if isinstance(value, (int, float)) and value <= 0:
            raise ValueError(
                f"Document option '{key}' in '{config_path}' must be greater than zero."
            )

        parsed[key] = value

    return parsed
