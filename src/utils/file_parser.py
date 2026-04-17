"""
Extract experimental parameters from oscilloscope CSV filenames.

Filename conventions (inside data/raw/D2_Optical_Pumping/0413/):
    B0.csv              -> Category 1  (zero-field baseline)
    70KHZ_RF.csv        -> Category 2  (low-field RF, freq <= 200 kHz)
    300KHZ_MAIN.csv     -> Category 3  (high-field / MAIN sweep)
    1000KHZ_MAIN_85.csv -> Category 3  (MAIN with isotope suffix)
"""

import os
import re


def parse_metadata(filename: str) -> dict:
    """
    Parse an oscilloscope CSV filename and return a metadata dictionary.

    Parameters
    ----------
    filename : str
        Bare filename (e.g. ``"70KHZ_RF.csv"``) or full path.

    Returns
    -------
    dict
        ``rf_freq``             – RF frequency in Hz (int), or 0 for B0, or
                                  None for unrecognised files.
        ``main_field_current``  – Placeholder (None); to be filled manually or
                                  derived from the CH3 ramp later.
        ``category``            – 1, 2, 3, or None if the filename is not
                                  recognised.
    """
    basename = os.path.basename(filename)
    name = os.path.splitext(basename)[0]

    # --- Category 1: zero-field baseline ---
    if name.upper() == "B0":
        return {"rf_freq": 0, "main_field_current": None, "category": 1}

    # --- Try *KHZ_RF (no MAIN keyword) ---
    rf_match = re.match(r"^(\d+)KHZ_RF$", name, re.IGNORECASE)
    if rf_match:
        freq_hz = int(rf_match.group(1)) * 1000
        if freq_hz <= 200_000:
            return {"rf_freq": freq_hz, "main_field_current": None, "category": 2}
        else:
            return {"rf_freq": freq_hz, "main_field_current": None, "category": 3}

    # --- Try *KHZ_MAIN* ---
    main_match = re.match(r"^(\d+)KHZ_MAIN", name, re.IGNORECASE)
    if main_match:
        freq_hz = int(main_match.group(1)) * 1000
        if freq_hz <= 200_000:
            return {"rf_freq": freq_hz, "main_field_current": None, "category": 2}
        return {"rf_freq": freq_hz, "main_field_current": None, "category": 3}

    # --- Unrecognised ---
    return {"rf_freq": None, "main_field_current": None, "category": None}
