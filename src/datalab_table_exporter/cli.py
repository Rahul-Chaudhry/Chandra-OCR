"""Command-line interface for the table exporter."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import requests

from .converter import DatalabConversionError, convert_to_excel


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert a PDF, JPG, or JPEG with Datalab and save its tables to Excel."
    )
    parser.add_argument("input_file", type=Path, help="PDF, JPG, or JPEG file to convert.")
    parser.add_argument("--output", type=Path, help="Excel output path.")
    parser.add_argument(
        "--api-key",
        default=os.environ.get("DATALAB_API_KEY"),
        help="Datalab API key. Defaults to DATALAB_API_KEY.",
    )
    parser.add_argument(
        "--mode",
        choices=["lite", "fast", "balanced", "accurate"],
        default="accurate",
        help="Datalab processing mode (default: accurate).",
    )
    parser.add_argument(
        "--poll-seconds",
        type=float,
        default=5,
        help="Seconds to wait between status checks (default: 5).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.api_key:
        parser.error("Set DATALAB_API_KEY or pass --api-key.")

    try:
        output = convert_to_excel(
            args.input_file,
            args.api_key,
            args.output,
            mode=args.mode,
            poll_seconds=args.poll_seconds,
        )
    except (DatalabConversionError, FileNotFoundError, ValueError, requests.RequestException) as error:
        parser.exit(1, f"Error: {error}\n")

    print(f"Saved Excel workbook: {output}")
    return 0
