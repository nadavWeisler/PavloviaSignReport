---
title: 'PavloviaSignReport: A Python tool for generating participant reports from Pavlovia data exports'
tags:
  - Python
  - psychology
  - behavioral research
  - Pavlovia
  - report generation
authors:
  - name: Nadav Weisler
    affiliation: 1
affiliations:
  - name: Independent Researcher
    index: 1
date: 2026-04-16
bibliography: paper.bib
---

# Summary

`PavloviaSignReport` is a Python command-line tool that automates the
generation of participant report documents from CSV exports produced by
the Pavlovia online experiment platform [@peirce2019psychopy2]. After a
behavioural or psychological experiment is completed on Pavlovia, researchers
often need to generate participant-facing or administrative reports that
combine text fields and signature data. Manually creating Word documents for
each participant is time-consuming and error-prone.

`PavloviaSignReport` reads a Pavlovia CSV export, extracts configurable
columns (text fields such as phone numbers, and base64-encoded signature
images), and automatically produces:

1. One `.docx` file per participant, containing a heading, selected text
   fields, and embedded signature images.
2. A `summary.docx` file that collates all rows into a single table, enabling
   efficient review.

The tool is column-agnostic: researchers can point it at *any* CSV file and
specify which columns to include — either through a JSON configuration file
passed on the command line or by editing the built-in defaults. Both document
and table image dimensions are configurable, and all temporary files are
handled safely so that concurrent runs do not conflict.

# Statement of Need

Online behavioural research platforms such as Pavlovia provide rich data
exports, but post-session reporting workflows are often still manual. Lab
managers and research assistants may need to open each row of a spreadsheet,
copy values into a report template, embed saved signature images, and repeat
this process for every participant. For studies with dozens or hundreds of
participants, this manual effort is both a bottleneck and a source of errors.

`PavloviaSignReport` addresses this gap by providing a lightweight, scriptable
tool that integrates directly with standard Pavlovia CSV exports and the
widely used `python-docx` library [@python-docx], making it straightforward to
adopt in existing research workflows.

# Functionality

## Inputs

- **CSV export** (`--file`): any comma-separated file produced by Pavlovia
  (or any other source with similarly structured columns).
- **Column configuration** (`--config`): an optional JSON file that lists
  which columns to include and whether each is plain text (`"type": "string"`)
  or a base64-encoded image (`"type": "image"`). When omitted the tool falls
  back to sensible defaults suitable for standard payment-signature exports.
- **Document settings**: `--id-col` selects the column used to name each
  output file; `--title` sets the heading text; `--results-folder` controls
  where files are saved.

## Outputs

- **Per-participant documents**: `{id_col_value}.docx` files saved to the
  results folder.
- **Summary table**: `summary.docx` containing a table with one row per
  participant and one column per configured field.

## Image handling

Participant signatures captured by PsychoPy/Pavlovia JavaScript plugins are
stored as data-URIs with a `data:image/<format>;base64,` prefix. The tool
strips this prefix with a generic regular expression that handles any image
format (PNG, JPEG, WebP, etc.) before embedding the decoded image into the
Word document. Error handling ensures that a failed image decode falls back
gracefully to plain text rather than aborting the run.

# Tests

The project includes a pytest [@pytest] test suite covering:

- `settings.py` — dataclass defaults and field validation.
- `document_creator.py` — image decoding, single-document generation, and
  summary-table generation (including graceful fallback on corrupt image data).
- `main.py` — CLI argument parsing, JSON config validation, cross-platform
  folder opening, and early-exit validation when required columns are absent.

Tests can be run with:

```bash
pytest tests/
```

# Acknowledgements

The author thanks all members of the lab whose administrative workflows
motivated the development of this tool.

# References
