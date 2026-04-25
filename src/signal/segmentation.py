"""
Segment a periodic CH3 sweep into individual rising-edge cycles.

The CH3 channel records a triangular / sawtooth ramp that drives the
main-field current.  Each rising edge (local minimum -> next local
maximum) constitutes one valid sweep cycle (~1 s).
"""

import numpy as np
from scipy.signal import find_peaks

# Physical constant: the maximum CH3 voltage after normalisation (V).
CH3_NORM_MAX = 0.917


def extract_valid_cycles(
    time_data,
    ch3_data,
    duration_range=(0.8, 1.2),
    min_distance_sec=0.5,
):
    """
    Normalise CH3 and extract valid rising-edge sweep segments.

    Parameters
    ----------
    time_data : array-like
        Absolute timestamps (s) from the oscilloscope.
    ch3_data : array-like
        Raw CH3 voltage readings.
    duration_range : tuple of float
        (min_seconds, max_seconds) accepted for one rising edge.

    Returns
    -------
    ch3_norm : np.ndarray
        Linearly normalised CH3 so that min = 0 V, max = 0.917 V.
    segments : list of (int, int)
        Each entry is ``(start_index, end_index)`` bounding one valid
        rising-edge cycle (inclusive on both ends).
    """
    time_data = np.asarray(time_data, dtype=float)
    ch3_data = np.asarray(ch3_data, dtype=float)

    # ---- 1. Linear normalisation: min -> 0 V, max -> 0.917 V ----
    ch3_min, ch3_max = ch3_data.min(), ch3_data.max()
    ch3_norm = (ch3_data - ch3_min) / (ch3_max - ch3_min) * CH3_NORM_MAX

    # ---- 2. Detect local extrema ----
    dt = float(time_data[1] - time_data[0])
    # Minimum distance between same-type extrema (≈ half the expected
    # full period, so we never double-count within a single half-cycle).
    min_distance = int(min_distance_sec / dt)
    # Prominence threshold: at least 20 % of the full normalised range
    # so that tiny noise bumps on the ramp are ignored.
    prom = 0.20 * CH3_NORM_MAX

    maxima_idx, _ = find_peaks(ch3_norm, distance=min_distance, prominence=prom)
    minima_idx, _ = find_peaks(-ch3_norm, distance=min_distance, prominence=prom)

    # ---- 3. Pair each minimum with its immediately following maximum ----
    segments = []
    for mi in minima_idx:
        candidates = maxima_idx[maxima_idx > mi]
        if candidates.size == 0:
            continue
        ma = candidates[0]

        duration = time_data[ma] - time_data[mi]
        if duration_range[0] <= duration <= duration_range[1]:
            segments.append((int(mi), int(ma)))

    return ch3_norm, segments
