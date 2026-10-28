"""Datalab conversion and Excel table export."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from io import StringIO
from pathlib import Path
from time import sleep
from typing import Any

import pandas as pd
import requests

API_URL = "https://www.datalab.to/api/v1/convert"
MIME_TYPES = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


class DatalabConversionError(RuntimeError):
    """Raised when Datalab cannot complete a conversion."""


def convert_to_excel(
    input_file: str | Path,
    api_key: str,
    output_file: str | Path | None = None,
    *,
    mode: str = "accurate",
    poll_seconds: float = 5,
    timeout: float = 60,
    sleep_fn: Callable[[float], None] = sleep,
) -> Path:
    """Convert one PDF/JPG/JPEG and write each detected table to an Excel sheet."""
    input_path = Path(input_file)
    mime_type = MIME_TYPES.get(input_path.suffix.lower())

    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if mime_type is None:
        allowed = ", ".join(MIME_TYPES)
        raise ValueError(f"Unsupported input type. Use one of: {allowed}")

    output_path = Path(output_file) if output_file else input_path.with_name(
        f"{input_path.stem}_tables.xlsx"
    )

    session = requests.Session()
    session.headers.update({"X-API-Key": api_key})

    with input_path.open("rb") as file:
        submission = session.post(
            API_URL,
            files={"file": (input_path.name, file, mime_type)},
            data={"output_format": "json", "mode": mode},
            timeout=timeout,
        )
    submission.raise_for_status()

    job = submission.json()
    check_url = job.get("request_check_url")
    if not check_url:
        raise DatalabConversionError("Datalab did not return a request_check_url.")

    result = _wait_for_result(session, check_url, poll_seconds, timeout, sleep_fn)
    tables = extract_tables(result)
    if not tables:
        raise DatalabConversionError("Datalab completed the conversion but found no tables.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_excel(tables, output_path)
    return output_path


def _wait_for_result(
    session: requests.Session,
    check_url: str,
    poll_seconds: float,
    timeout: float,
    sleep_fn: Callable[[float], None],
) -> dict[str, Any]:
    while True:
        response = session.get(check_url, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        status = result.get("status")

        if status == "complete":
            return result
        if status in {"failed", "error"}:
            message = result.get("error") or "Datalab did not provide an error message."
            raise DatalabConversionError(f"Datalab conversion failed: {message}")

        sleep_fn(poll_seconds)


def extract_tables(result: dict[str, Any]) -> list[pd.DataFrame]:
    """Extract all HTML table blocks from a completed Datalab response."""
    tables: list[pd.DataFrame] = []
    for block in _table_blocks(result.get("json", {})):
        html = block.get("html")
        if html:
            tables.extend(pd.read_html(StringIO(html)))
    return tables


def _table_blocks(item: Any) -> Iterator[dict[str, Any]]:
    if isinstance(item, dict):
        if item.get("block_type") == "Table":
            yield item
        for value in item.values():
            yield from _table_blocks(value)
    elif isinstance(item, list):
        for value in item:
            yield from _table_blocks(value)


def write_excel(tables: list[pd.DataFrame], output_path: Path) -> None:
    """Write every DataFrame to its own worksheet without pandas MultiIndex errors."""
    with pd.ExcelWriter(output_path) as writer:
        for index, table in enumerate(tables, start=1):
            _flatten_columns(table).to_excel(writer, sheet_name=f"Table_{index}", index=False)


def _flatten_columns(table: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(table.columns, pd.MultiIndex):
        return table

    flattened = table.copy()
    flattened.columns = [
        " | ".join(
            dict.fromkeys(
                str(part) for part in column if not str(part).startswith("Unnamed")
            )
        )
        for column in table.columns
    ]
    return flattened
