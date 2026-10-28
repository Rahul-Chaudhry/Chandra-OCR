# Chandra OCR

Convert PDFs, JPGs, and JPEGs with Datalab, then export every detected table
to an Excel workbook.

## Start in JupyterLab

Clone the repository, create a virtual environment, and install JupyterLab:

    git clone https://github.com/Rahul-Chaudhry/Chandra-OCR.git
    cd Chandra-OCR
    python3 -m venv .venv
    source .venv/bin/activate
    python3 -m pip install jupyterlab
    jupyter lab

On Windows PowerShell, activate the environment with:

    .venv\Scripts\Activate.ps1

Open a notebook from the notebooks folder. Each notebook begins with a
commented, one-package-per-line install cell. If a package is missing,
remove the leading # from its line and run that cell once.

## Notebooks

- batch_convert_to_excel.ipynb processes every supported source file in data
  and writes one Excel workbook per input to outputs.
- single_file_convert_to_excel.ipynb processes the one file named in
  INPUT_FILENAME, saves its Datalab JSON response, and writes its Excel
  workbook to outputs.

Put PDFs, JPGs, or JPEGs in data. Add a Datalab API key in the notebook or
set DATALAB_API_KEY in your local environment. Each detected table becomes a
Table_1, Table_2, and so on worksheet. Supported inputs are .pdf, .jpg, and
.jpeg.

## Project layout

    data/          Source PDFs and images
    outputs/       Generated JSON and Excel workbooks, ignored by Git
    notebooks/     All executable project workflows
    documentation/ Project documentation and references

## Notes

- Keep API keys local; .env is ignored by Git.
- The exporter flattens multi-level headers before writing Excel, avoiding
  pandas' MultiIndex index=False limitation.

See the [Datalab Convert API reference](https://documentation.datalab.to/api-reference/convert-document)
for details about the upstream conversion service.
