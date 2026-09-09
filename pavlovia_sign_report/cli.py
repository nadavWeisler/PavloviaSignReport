"""Command-line interface for PavloviaSignReport."""

from __future__ import annotations

import argparse
import logging
import os
import platform
import subprocess
import sys
from collections.abc import Sequence

from pavlovia_sign_report.app import generate_reports, read_input_data
from pavlovia_sign_report.config import (
    DEFAULT_COLUMNS,
    DEFAULT_FILE,
    DEFAULT_ID_COL,
    DEFAULT_RESULTS_FOLDER,
    DEFAULT_TITLE,
    load_config,
)
from pavlovia_sign_report.models import DocumentSettings, ReportConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def open_folder(path: str) -> None:
    """Open a folder in the system file explorer."""

    if not os.path.isdir(path):
        raise ValueError(f"'{path}' is not an existing directory.")

    system = platform.system()
    if system == "Windows":
        os.startfile(path)  # noqa: S606
    elif system == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(
        description="Generate participant Word documents from a Pavlovia CSV export."
    )
    parser.add_argument(
        "--file",
        default=DEFAULT_FILE,
        help=f"Path to the CSV file (default: {DEFAULT_FILE})",
    )
    parser.add_argument(
        "--id-col",
        default=DEFAULT_ID_COL,
        help=f"Column used as the participant identifier (default: {DEFAULT_ID_COL})",
    )
    parser.add_argument(
        "--title",
        default=None,
        help=(
            f"Document heading. Defaults to '{DEFAULT_TITLE}' unless "
            "overridden by config."
        ),
    )
    parser.add_argument(
        "--config",
        default=None,
        metavar="CONFIG_JSON",
        help="Optional JSON file defining report columns and document settings.",
    )
    parser.add_argument(
        "--results-folder",
        default=DEFAULT_RESULTS_FOLDER,
        help=(
            "Folder where generated documents are saved "
            f"(default: {DEFAULT_RESULTS_FOLDER})"
        ),
    )
    parser.add_argument(
        "--summary-filename", default=None, help="Name of the summary .docx file."
    )
    parser.add_argument(
        "--output-template",
        default=None,
        help=(
            "Filename template for participant documents. Supports "
            "{id}, {safe_id}, {row_number}, and CSV column names."
        ),
    )
    parser.add_argument(
        "--document-intro",
        default=None,
        help=(
            "Optional paragraph added below the title in each participant "
            "document. Supports the same placeholders as --output-template."
        ),
    )
    parser.add_argument(
        "--image-width",
        type=float,
        default=None,
        help="Width of participant images in inches.",
    )
    parser.add_argument(
        "--image-height",
        type=float,
        default=None,
        help="Height of participant images in inches.",
    )
    parser.add_argument(
        "--table-image-width",
        type=float,
        default=None,
        help="Width of summary-table images in inches.",
    )
    parser.add_argument(
        "--table-image-height",
        type=float,
        default=None,
        help="Height of summary-table images in inches.",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the results folder when generation is complete.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs without generating documents.",
    )
    return parser.parse_args(argv)


def build_document_settings(
    args: argparse.Namespace, config: ReportConfig
) -> DocumentSettings:
    """Merge defaults, config, and CLI options into final document settings."""

    settings = {
        "title": DEFAULT_TITLE,
        "image_width": 4.0,
        "image_height": 3.0,
        "table_image_width": 2.0,
        "table_image_height": 2.0,
        "summary_filename": "summary.docx",
        "output_filename_template": "{safe_id}.docx",
        "document_intro": None,
    }
    settings.update(config.document)

    overrides = {
        "title": args.title,
        "image_width": args.image_width,
        "image_height": args.image_height,
        "table_image_width": args.table_image_width,
        "table_image_height": args.table_image_height,
        "summary_filename": args.summary_filename,
        "output_filename_template": args.output_template,
        "document_intro": args.document_intro,
    }
    for key, value in overrides.items():
        if value is not None:
            settings[key] = value

    for key in (
        "image_width",
        "image_height",
        "table_image_width",
        "table_image_height",
    ):
        if float(settings[key]) <= 0:
            raise ValueError(f"'{key}' must be greater than zero.")

    return DocumentSettings(id_col=args.id_col, **settings)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI."""

    args = parse_args(argv)
    try:
        config = (
            load_config(args.config)
            if args.config
            else ReportConfig(columns=list(DEFAULT_COLUMNS))
        )
        document_settings = build_document_settings(args, config)
        dataframe = read_input_data(args.file)
        summary = generate_reports(
            dataframe,
            args.results_folder,
            config.columns,
            document_settings,
            dry_run=args.dry_run,
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        logger.info(
            "Validation succeeded for %s rows. Output would be written to '%s'.",
            summary.rows_processed,
            args.results_folder,
        )
    elif args.open:
        open_folder(args.results_folder)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
