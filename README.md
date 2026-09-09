# PavloviaSignReport

`PavloviaSignReport` is a Python package and command-line tool for creating
participant report documents from Pavlovia CSV exports.

It reads configurable CSV columns and generates:

- one `.docx` file per participant
- one summary `.docx` table across all rows

It is designed for research workflows that need fast, repeatable report
generation from online experiment data.

## Installation

Install the package locally:

```bash
python -m pip install .
```

For development, install the package with test and lint dependencies:

```bash
python -m pip install -e .[dev]
```

If you only want the runtime dependencies, `requirements.txt` now contains the
minimal runtime set used by the package.

## Usage

You can run the packaged CLI in either form:

```bash
python -m pavlovia_sign_report [OPTIONS]
pavlovia-sign-report [OPTIONS]
```

The legacy entry point still works:

```bash
python main.py [OPTIONS]
```

### Common options

| Flag | Default | Description |
|------|---------|-------------|
| `--file PATH` | `./examples/input/payment.csv` | Path to the CSV export file |
| `--id-col COL` | `num` | Column used as the participant identifier |
| `--title TEXT` | built-in default or config value | Heading at the top of every participant document |
| `--config PATH` | built-in defaults | JSON file defining columns and optional document settings |
| `--results-folder DIR` | `results` | Folder where generated documents are saved |
| `--summary-filename NAME` | `summary.docx` | Summary document filename |
| `--output-template TEMPLATE` | `{safe_id}.docx` | Output filename template for participant documents |
| `--document-intro TEXT` | off | Optional paragraph added below the title in each participant document |
| `--image-width FLOAT` | `4.0` | Participant image width in inches |
| `--image-height FLOAT` | `3.0` | Participant image height in inches |
| `--table-image-width FLOAT` | `2.0` | Summary-table image width in inches |
| `--table-image-height FLOAT` | `2.0` | Summary-table image height in inches |
| `--dry-run` | off | Validate inputs without generating documents |
| `--open` | off | Open the results folder when done |

### Example

The default column mapping matches the synthetic payment fixture:

```bash
python -m pavlovia_sign_report \
  --file ./examples/input/payment.csv \
  --id-col num \
  --results-folder ./results
```

The package-format config example matches the synthetic Pavlovia-style
fixtures:

```bash
python -m pavlovia_sign_report \
  --file ./examples/input/file.csv \
  --id-col id \
  --config ./examples/config/report_config.json \
  --results-folder ./results
```

### Dry-run validation

Use dry-run mode before generating files when working with a new export or
configuration:

```bash
python -m pavlovia_sign_report --dry-run
```

## Sample data

Checked-in sample data is synthetic only:

- `examples/input/payment.csv` — default CLI mapping (`block/payment_phone.text1` is the phone field)
- `examples/input/file.csv` and `examples/input/rec.csv` — Pavlovia-style survey exports
- `examples/output/results.zip` — sample documents generated from the payment fixture

They use fake names, IDs, phone numbers, and email addresses, plus generated
placeholder signature images. Root-level `payment.csv`, `file.csv`, `rec.csv`,
and `results.zip` are gitignored so a live export dropped on those paths
cannot be re-committed.

## Configuration

`--config` accepts either:

1. the legacy format: a JSON array of column objects
2. the package format: a JSON object with `columns` and optional `document`
   sections

An example package-format config is provided at
`examples/config/report_config.json`.

### Package config format

```json
{
  "document": {
    "title": "Participant Report",
    "summary_filename": "participants-summary.docx",
    "output_filename_template": "participant-{safe_id}.docx",
    "document_intro": "Thank you {name} for participating.",
    "image_width": 4,
    "image_height": 3,
    "table_image_width": 1.5,
    "table_image_height": 1.5
  },
  "columns": [
    {"name": "name", "display_name": "Participant Name", "type": "string"},
    {"name": "amount", "display_name": "Amount", "type": "number"},
    {
      "name": "isComplete",
      "display_name": "Completed",
      "type": "boolean",
      "true_text": "Complete",
      "false_text": "Incomplete"
    },
    {"name": "sign", "display_name": "Signature", "type": "image"}
  ]
}
```

### Column fields

Each column object supports:

- `name` — CSV column name
- `display_name` — label shown in the document
- `type` — one of `string`, `image`, `number`, `boolean`
- `required` — whether missing values should fail validation (defaults to `true`)
- `true_text` / `false_text` — optional labels for boolean columns

### Template placeholders

`output_filename_template` and `document_intro` support:

- `{id}` — raw participant identifier
- `{safe_id}` — sanitized identifier used for filenames
- `{row_number}` — 1-based CSV row number
- any CSV column name, for example `{name}`

## Validation and troubleshooting

The tool now validates inputs before writing files and reports clear errors for:

- missing CSV columns
- empty required values
- malformed participant IDs that cannot produce safe filenames
- duplicate participant IDs or duplicate generated filenames
- invalid or empty base64 image data
- unsupported config keys or invalid config value types

If you are integrating a new export, start with `--dry-run` and confirm the
configured column names match the CSV headers.

## Examples

- Config example: `examples/config/report_config.json`
- Synthetic input fixtures: `examples/input/`
- Synthetic output sample: `examples/output/results.zip`

## Testing

Run tests with:

```bash
python -m pytest tests/
```

Run lint with:

```bash
python -m ruff check .
```

A GitHub Actions workflow in `.github/workflows/ci.yml` runs both on pushes and
pull requests.

## Citation

This repository includes JOSS manuscript files (`paper.md`, `paper.bib`) and a
`CITATION.cff` file.

## License

MIT (see `LICENSE`).
