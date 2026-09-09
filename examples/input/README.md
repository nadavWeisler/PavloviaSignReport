Synthetic fixture CSVs for running the packaged CLI without live participant
data:

- `payment.csv` — default CLI mapping (`--id-col num`).
  `block/payment_phone.text1` holds the phone values that
  `DEFAULT_COLUMNS` renders as מספר טלפון.
- `file.csv` / `rec.csv` — Pavlovia-style survey exports used with
  `examples/config/report_config.json`.

Keep live Pavlovia exports out of git. Root-level `payment.csv`, `file.csv`,
`rec.csv`, and `results.zip` are gitignored so replacing them with a real
export cannot be committed by `git add -u`.
