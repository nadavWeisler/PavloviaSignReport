"""End-to-end CLI tests."""

import subprocess
import sys
from pathlib import Path


def test_cli_generates_documents(
    repo_root: Path, sample_csv: Path, sample_config: Path, tmp_path: Path
):
    results_dir = tmp_path / "results"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pavlovia_sign_report",
            "--file",
            str(sample_csv),
            "--id-col",
            "id",
            "--config",
            str(sample_config),
            "--results-folder",
            str(results_dir),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert (results_dir / "report-participant_1.docx").exists()
    assert (results_dir / "report-participant_2.docx").exists()
    assert (results_dir / "summary-output.docx").exists()


def test_cli_dry_run_reports_validation_errors(
    repo_root: Path,
    sample_csv: Path,
    sample_config: Path,
    tmp_path: Path,
):
    broken_csv = tmp_path / "broken.csv"
    broken_csv.write_text(
        sample_csv.read_text(encoding="utf-8").replace("Bob", ""), encoding="utf-8"
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pavlovia_sign_report",
            "--file",
            str(broken_csv),
            "--id-col",
            "id",
            "--config",
            str(sample_config),
            "--results-folder",
            str(tmp_path / "results"),
            "--dry-run",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "required column 'name' is empty" in completed.stderr


def test_synthetic_payment_fixture_is_the_cli_default(repo_root: Path):
    completed = subprocess.run(
        [sys.executable, "-m", "pavlovia_sign_report", "--dry-run"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Validation succeeded" in completed.stderr


def test_synthetic_file_fixture_dry_run(repo_root: Path):
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pavlovia_sign_report",
            "--file",
            str(repo_root / "examples" / "input" / "file.csv"),
            "--id-col",
            "id",
            "--config",
            str(repo_root / "examples" / "config" / "report_config.json"),
            "--dry-run",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Validation succeeded" in completed.stderr
