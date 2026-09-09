"""Core report generation workflow."""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from tqdm import tqdm

from pavlovia_sign_report.document_creator import (
    create_doc_with_table,
    create_single_doc,
    render_template,
    render_value,
    validate_image_value,
)
from pavlovia_sign_report.models import ColumnSettings, ColumnType, DocumentSettings

logger = logging.getLogger(__name__)

_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


@dataclass(slots=True)
class RunSummary:
    """Summary of a report run."""

    rows_processed: int
    results_folder: str
    summary_path: str | None
    document_paths: list[str]


def read_input_data(file_path: str) -> pd.DataFrame:
    """Read the CSV input file with user-friendly errors."""

    try:
        dataframe = pd.read_csv(file_path)
    except FileNotFoundError as exc:
        raise ValueError(f"CSV file '{file_path}' does not exist.") from exc
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"CSV file '{file_path}' is empty.") from exc
    except pd.errors.ParserError as exc:
        raise ValueError(f"CSV file '{file_path}' could not be parsed: {exc}.") from exc

    if dataframe.empty:
        raise ValueError(
            f"CSV file '{file_path}' does not contain any participant rows."
        )

    return dataframe


def sanitize_filename(value: Any) -> str:
    """Create a filesystem-safe filename stem."""

    text = str(value).strip()
    text = _INVALID_FILENAME_CHARS.sub("_", text)
    text = text.replace(os.sep, "_")
    if os.altsep:
        text = text.replace(os.altsep, "_")
    text = text.strip(" .")
    text = re.sub(r"\s+", " ", text)
    return text


def generate_reports(
    dataframe: pd.DataFrame,
    results_folder: str,
    columns: list[ColumnSettings],
    document_settings: DocumentSettings,
    *,
    dry_run: bool = False,
) -> RunSummary:
    """Validate inputs and generate participant and summary documents."""

    validation = validate_dataframe(
        dataframe,
        columns,
        document_settings,
        results_folder=results_folder,
    )
    if dry_run:
        return RunSummary(
            rows_processed=len(dataframe),
            results_folder=results_folder,
            summary_path=None,
            document_paths=validation.document_paths,
        )

    os.makedirs(results_folder, exist_ok=True)
    document_paths: list[str] = []
    intro_template = document_settings.document_intro
    iterator = tqdm(dataframe.iterrows(), total=dataframe.shape[0])
    for row_number, (_, row) in enumerate(iterator, start=1):
        output_path = validation.document_paths[row_number - 1]
        intro_text = (
            render_template(
                intro_template,
                row,
                validation.template_contexts[row_number - 1],
            )
            if intro_template
            else None
        )
        create_single_doc(
            row,
            output_path,
            columns,
            document_settings,
            intro_text=intro_text,
        )
        document_paths.append(output_path)

    summary_path = str(Path(results_folder) / validation.summary_filename)
    create_doc_with_table(dataframe, summary_path, columns, document_settings)
    logger.info("Documents saved to '%s'.", results_folder)

    return RunSummary(
        rows_processed=len(dataframe),
        results_folder=results_folder,
        summary_path=summary_path,
        document_paths=document_paths,
    )


@dataclass(slots=True)
class ValidationResult:
    document_paths: list[str]
    template_contexts: list[dict[str, str]]
    summary_filename: str


def validate_dataframe(
    dataframe: pd.DataFrame,
    columns: list[ColumnSettings],
    document_settings: DocumentSettings,
    *,
    results_folder: str = "",
) -> ValidationResult:
    """Validate input data before document generation."""

    missing = []
    if document_settings.id_col not in dataframe.columns:
        missing.append(f"id column '{document_settings.id_col}'")
    missing_columns = [
        column.name for column in columns if column.name not in dataframe.columns
    ]
    if missing_columns:
        missing.append(f"columns {missing_columns}")
    if missing:
        raise ValueError(
            "The following expected columns are missing: "
            + ", ".join(missing)
            + f". Available columns: {list(dataframe.columns)}"
        )

    if not columns:
        raise ValueError(
            "At least one column must be configured before generating reports."
        )

    summary_filename = _sanitize_output_filename(
        _normalize_docx_filename(
            document_settings.summary_filename,
            label="summary filename",
        )
    )
    if not summary_filename:
        raise ValueError("The summary filename is empty after sanitization.")
    seen_raw_ids: dict[str, int] = {}
    seen_output_paths: dict[str, int] = {}
    document_paths: list[str] = []
    template_contexts: list[dict[str, str]] = []
    errors: list[str] = []

    for row_number, (_, row) in enumerate(dataframe.iterrows(), start=1):
        raw_id = row[document_settings.id_col]
        raw_id_text = _normalize_required_value(
            raw_id, document_settings.id_col, row_number, errors
        )
        if raw_id_text is None:
            continue

        if raw_id_text in seen_raw_ids:
            errors.append(
                f"Row {row_number}: duplicate participant id '{raw_id_text}' "
                f"also appears on row {seen_raw_ids[raw_id_text]}."
            )
        else:
            seen_raw_ids[raw_id_text] = row_number

        safe_id = sanitize_filename(raw_id_text)
        if not safe_id:
            errors.append(
                f"Row {row_number}: participant id '{raw_id_text}' does not "
                "produce a safe output filename."
            )
            continue

        template_context = {
            "id": raw_id_text,
            "safe_id": safe_id,
            "row_number": str(row_number),
        }
        try:
            output_filename = render_template(
                document_settings.output_filename_template,
                row,
                template_context,
            )
        except ValueError as exc:
            errors.append(f"Row {row_number}: {exc}")
            continue

        output_filename = _normalize_docx_filename(
            output_filename, label="output filename"
        )
        output_filename = _sanitize_output_filename(output_filename)
        if not output_filename:
            errors.append(
                f"Row {row_number}: output filename is empty after sanitization."
            )
            continue

        if output_filename in seen_output_paths:
            errors.append(
                f"Row {row_number}: output filename '{output_filename}' "
                f"duplicates row {seen_output_paths[output_filename]}."
            )
        else:
            seen_output_paths[output_filename] = row_number

        for column in columns:
            value = row[column.name]
            if _is_missing(value):
                if column.required:
                    errors.append(
                        f"Row {row_number}: required column '{column.name}' is empty."
                    )
                continue

            if column.column_type == ColumnType.IMAGE:
                try:
                    validate_image_value(str(value))
                except ValueError as exc:
                    errors.append(f"Row {row_number}: column '{column.name}' {exc}")
                continue

            try:
                render_value(value, column)
            except ValueError as exc:
                errors.append(f"Row {row_number}: {exc}")

        document_paths.append(str(Path(results_folder) / output_filename))
        template_contexts.append(template_context)

    if errors:
        raise ValueError("Validation failed:\n- " + "\n- ".join(errors))

    return ValidationResult(
        document_paths=document_paths,
        template_contexts=template_contexts,
        summary_filename=summary_filename,
    )


def _normalize_required_value(
    value: Any, column_name: str, row_number: int, errors: list[str]
) -> str | None:
    if _is_missing(value):
        errors.append(f"Row {row_number}: required id column '{column_name}' is empty.")
        return None
    text = str(value).strip()
    if not text:
        errors.append(f"Row {row_number}: required id column '{column_name}' is empty.")
        return None
    return text


def _is_missing(value: Any) -> bool:
    return pd.isna(value) or (isinstance(value, str) and not value.strip())


def _normalize_docx_filename(value: str, *, label: str) -> str:
    text = value.strip()
    if not text:
        raise ValueError(f"The {label} must not be empty.")
    if not text.lower().endswith(".docx"):
        text = f"{text}.docx"
    return text


def _sanitize_output_filename(filename: str) -> str:
    path = Path(filename)
    stem = sanitize_filename(path.stem)
    suffix = path.suffix or ".docx"
    if not stem:
        return ""
    return f"{stem}{suffix}"
