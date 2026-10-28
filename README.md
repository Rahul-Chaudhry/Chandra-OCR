# Chandra OCR

Convert a PDF, JPG, or JPEG with Datalab and save each detected table to a separate worksheet in an Excel workbook.

The project keeps the workflow intentionally small:

1. Upload one supported file to Datalab's Convert API.
2. Poll the job until it finishes.
3. Read the HTML returned for every table block.
4. Export each table to a `Table_1`, `Table_2`, … worksheet.

The exporter flattens multi-level table headers before writing Excel. That avoids pandas' `NotImplementedError` for MultiIndex columns when `index=False`.

## Requirements

- Python 3.10 or newer
- A Datalab API key

## Run the notebook (beginner setup)

The quickest route is the ready-to-run notebook at
[`notebooks/batch_convert_to_excel.ipynb`](notebooks/batch_convert_to_excel.ipynb). It
processes every PDF, JPG, and JPEG in the project folder and creates one
`*_tables.xlsx` workbook for each input file.

Open Terminal and run these commands once:

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

Then, in the browser window that opens:

1. Put your PDF, JPG, or JPEG files in the `Chandra-OCR` project folder.
2. Open `notebooks/batch_convert_to_excel.ipynb`.
3. Paste your Datalab key into the `API_KEY` line in the settings cell. Keep that local change out of Git.
4. Select **Run All Cells**.

The `requirements.txt` file installs JupyterLab and every library the notebook
needs: pandas, requests, lxml, and openpyxl. The notebook filters its folder to
supported input types, so it will not try to upload itself, the README, or the
Excel workbooks it creates.

## Install

```bash
git clone https://github.com/Rahul-Chaudhry/Chandra-OCR.git
cd Chandra-OCR
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

On Windows PowerShell, activate the virtual environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Set your API key

macOS/Linux:

```bash
export DATALAB_API_KEY="your_api_key"
```

Windows PowerShell:

```powershell
$env:DATALAB_API_KEY = "your_api_key"
```

The key is read from the environment by default. You can instead pass `--api-key` for a one-off run, but environment variables avoid putting the key into shell history or source files.

## Convert a file

```bash
datalab-tables "1913 Tunisie-15.pdf"
```

This writes `1913 Tunisie-15_tables.xlsx` beside the input file.

Choose an output path, processing mode, or polling interval when needed:

```bash
datalab-tables scan.jpeg \
  --output exports/scan_tables.xlsx \
  --mode accurate \
  --poll-seconds 5
```

Supported input extensions are `.pdf`, `.jpg`, and `.jpeg`.

## Use from a notebook or another Python script

```python
from datalab_table_exporter import convert_to_excel

output = convert_to_excel(
    "1913 Tunisie-15.pdf",
    api_key="your_api_key",
)

print(output)
```

## Run tests

```bash
pytest
```

## Project layout

```text
src/datalab_table_exporter/
  converter.py  # Datalab upload, polling, parsing, and Excel export
  cli.py        # datalab-tables command
notebooks/
  batch_convert_to_excel.ipynb  # Batch PDF/JPG/JPEG conversion in Jupyter
requirements.txt  # Jupyter notebook dependencies
tests/
  test_converter.py
```

## Notes

- The project does not save Datalab's raw JSON response. The result stays in memory only long enough to create the Excel workbook.
- A failed Datalab job raises an error instead of waiting forever.
- The Datalab Convert API supports document and image conversion; its current reference describes PDF and image uploads and the `accurate` processing mode used here. See the [Datalab Convert API reference](https://documentation.datalab.to/api-reference/convert-document).
