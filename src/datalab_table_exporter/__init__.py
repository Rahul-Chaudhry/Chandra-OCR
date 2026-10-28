"""Convert Datalab table blocks into Excel worksheets."""

from .converter import DatalabConversionError, convert_to_excel

__all__ = ["DatalabConversionError", "convert_to_excel"]
