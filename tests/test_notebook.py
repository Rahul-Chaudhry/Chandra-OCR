import json
from pathlib import Path


NOTEBOOK = Path("notebooks/batch_convert_to_excel.ipynb")


def test_batch_notebook_is_valid_and_runnable_python() -> None:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    code = "\n".join(
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    )

    compile(code, str(NOTEBOOK), "exec")
    assert notebook["nbformat"] == 4
    assert 'API_KEY = ""' in code
    assert '".pdf"' in code
    assert '".jpg"' in code
    assert '".jpeg"' in code
