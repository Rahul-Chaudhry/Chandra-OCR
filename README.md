# Chandra OCR

Convert PDFs, JPGs, and JPEGs with Datalab, then export every detected table to
its own worksheet in an Excel workbook.

## Quick start

```bash
git clone https://github.com/Rahul-Chaudhry/Chandra-OCR.git
cd Chandra-OCR
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
jupyter lab
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Notebook workflow

1. Put PDFs, JPGs, or JPEGs in `data/`.
2. Open `notebooks/batch_convert_to_excel.ipynb` in JupyterLab.
3. Add your Datalab API key to `API_KEY`, or set `DATALAB_API_KEY` in Terminal.
4. Select **Run All Cells**.

The notebook processes every supported file in `data/` and saves a separate
`*_tables.xlsx` workbook for each input in `outputs/`. Each detected table
becomes a `Table_1`, `Table_2`, and so on worksheet.

## Command-line workflow

Install the command-line package when you prefer Terminal over Jupyter:

```bash
python -m pip install -e .
export DATALAB_API_KEY="your_api_key"
datalab-tables data/scan.jpeg --output outputs/scan_tables.xlsx
```

On Windows PowerShell:

```powershell
$env:DATALAB_API_KEY = "your_api_key"
```

Use `--mode accurate` or `--poll-seconds 5` when needed. Supported inputs are
`.pdf`, `.jpg`, and `.jpeg`.

## Project layout

```text
data/          # Add source PDFs and images here
outputs/       # Generated Excel workbooks (ignored by Git)
notebooks/     # Beginner-friendly Jupyter workflow
src/           # Reusable converter and command-line package
documentation/ # Project documentation and references
requirements.txt
```

## Notes

- Keep API keys local; `.env` is ignored by Git.
- The exporter flattens multi-level headers before writing Excel, avoiding
  pandas' MultiIndex `index=False` limitation.
- The raw Datalab JSON result stays in memory and is not written to disk.

See the [Datalab Convert API reference](https://documentation.datalab.to/api-reference/convert-document)
for details about the upstream conversion service.
