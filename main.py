"""Backwards-compatible entry point for PavloviaSignReport."""

from __future__ import annotations

from collections.abc import Sequence

from pavlovia_sign_report.cli import (
    main as _main,
)
from pavlovia_sign_report.cli import (
    open_folder as _open_folder,
)
from pavlovia_sign_report.cli import (
    parse_args as _parse_args,
)
from pavlovia_sign_report.config import (
    load_columns_from_config as _load_columns_from_config,
)


def parse_args(argv: Sequence[str] | None = None):
    return _parse_args(argv)


def open_folder(path: str) -> None:
    _open_folder(path)


def load_columns_from_config(config_path: str):
    return _load_columns_from_config(config_path)


def main(argv: Sequence[str] | None = None) -> int:
    return _main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
