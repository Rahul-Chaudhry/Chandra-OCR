from pathlib import Path

import pandas as pd
import pytest

from datalab_table_exporter import converter


TABLE_HTML = """
<table>
  <thead>
    <tr><th rowspan="2">Place</th><th colspan="2">Population</th></tr>
    <tr><th>1906</th><th>1911</th></tr>
  </thead>
  <tbody><tr><td>Tunis</td><td>18626</td><td>23904</td></tr></tbody>
</table>
"""


def test_extract_tables_finds_nested_table_blocks() -> None:
    result = {
        "json": {
            "children": [
                {
                    "block_type": "Page",
                    "children": [{"block_type": "Table", "html": TABLE_HTML}],
                }
            ]
        }
    }

    tables = converter.extract_tables(result)

    assert len(tables) == 1
    assert tables[0].iloc[0, 0] == "Tunis"


def test_write_excel_flattens_multiindex_columns(tmp_path: Path) -> None:
    table = pd.DataFrame(
        [["Tunis", 18626, 23904]],
        columns=pd.MultiIndex.from_tuples(
            [("Place", "Place"), ("Population", "1906"), ("Population", "1911")]
        ),
    )
    output = tmp_path / "tables.xlsx"

    converter.write_excel([table], output)

    exported = pd.read_excel(output, sheet_name="Table_1")
    assert list(exported.columns) == ["Place", "Population | 1906", "Population | 1911"]
    assert exported.iloc[0, 0] == "Tunis"


def test_convert_to_excel_submits_jpeg_and_polls(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "scan.jpeg"
    source.write_bytes(b"image data")
    output = tmp_path / "result.xlsx"
    sleeps: list[float] = []

    class Response:
        def __init__(self, payload: dict) -> None:
            self.payload = payload

        def json(self) -> dict:
            return self.payload

        def raise_for_status(self) -> None:
            return None

    class Session:
        def __init__(self) -> None:
            self.headers: dict[str, str] = {}
            self.post_args: dict | None = None
            self.statuses = [
                Response({"status": "processing"}),
                Response({"status": "complete", "json": {}}),
            ]

        def post(self, *args, **kwargs):
            self.post_args = kwargs
            return Response({"request_check_url": "https://example.test/status"})

        def get(self, *args, **kwargs):
            return self.statuses.pop(0)

    session = Session()
    monkeypatch.setattr(converter.requests, "Session", lambda: session)
    monkeypatch.setattr(
        converter,
        "extract_tables",
        lambda _: [pd.DataFrame({"Place": ["Tunis"], "Population": [23904]})],
    )

    saved = converter.convert_to_excel(
        source,
        "test-key",
        output,
        poll_seconds=0.25,
        sleep_fn=sleeps.append,
    )

    assert saved == output
    assert output.is_file()
    assert session.headers == {"X-API-Key": "test-key"}
    assert session.post_args["files"]["file"][2] == "image/jpeg"
    assert sleeps == [0.25]


def test_convert_to_excel_rejects_other_input_types(tmp_path: Path) -> None:
    source = tmp_path / "scan.png"
    source.write_bytes(b"image data")

    with pytest.raises(ValueError, match="Unsupported input type"):
        converter.convert_to_excel(source, "test-key")
