"""Signal processing: segmentation and dip detection."""

from .segmentation import extract_valid_cycles
from .detection import detect_dips

__all__ = ["extract_valid_cycles", "detect_dips"]
