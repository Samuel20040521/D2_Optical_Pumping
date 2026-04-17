"""
Detect absorption dips in the CH2 (photodetector) signal within each
valid sweep cycle, then cluster dips across cycles by their relative
time position.

The raw CH2 waveform is smoothed with a moving-average filter before
peak detection to suppress ADC quantisation noise that would otherwise
create thousands of spurious local extrema.
"""

import numpy as np
import pandas as pd
from scipy.ndimage import uniform_filter1d
from scipy.signal import find_peaks


def detect_dips(
    time_data,
    ch2_data,
    ch3_norm,
    valid_segments,
    prominence=0.05,
    width=200,
    smooth_pts=501,
    min_dip_sep=0.01,
    cluster_threshold=0.05,
):
    """
    Find absorption dips in CH2 for every valid cycle and cluster them.

    Parameters
    ----------
    time_data : array-like
        Absolute timestamps (s).
    ch2_data : array-like
        Raw CH2 voltage (photodetector).
    ch3_norm : np.ndarray
        Normalised CH3 sweep (from ``extract_valid_cycles``).
    valid_segments : list of (int, int)
        Cycle boundaries from ``extract_valid_cycles``.
    prominence : float
        Minimum prominence (V) for a dip to be accepted.
    width : int or None
        Minimum peak width (samples) in the inverted signal.
    smooth_pts : int
        Window size (samples) for the moving-average smoother applied
        to the inverted CH2 before peak detection.  Must be odd.
    min_dip_sep : float
        Minimum time separation (s) between distinct dips inside a
        single cycle.  Translated to a ``distance`` in samples.
    cluster_threshold : float
        Maximum gap in relative time (s) between consecutive dips that
        are still grouped into the same cluster.

    Returns
    -------
    pd.DataFrame
        Columns: ``Cycle``, ``Relative_Time``, ``CH2_Depth``,
        ``CH3_Voltage``, ``Group``.
        One row per individual dip detection; the ``Group`` column
        identifies which physical resonance each dip belongs to across
        cycles.
    """
    time_data = np.asarray(time_data, dtype=float)
    ch2_data = np.asarray(ch2_data, dtype=float)

    dt = float(time_data[1] - time_data[0])
    min_distance = max(1, int(min_dip_sep / dt))

    all_dips = []

    for cycle_idx, (start, end) in enumerate(valid_segments):
        t_seg   = time_data[start : end + 1]
        ch2_seg = ch2_data[start : end + 1]
        ch3_seg = ch3_norm[start : end + 1]

        rel_time = t_seg - t_seg[0]

        # Smooth the inverted signal to suppress quantisation noise
        inverted = uniform_filter1d(-ch2_seg, size=smooth_pts)

        peaks, props = find_peaks(
            inverted,
            prominence=prominence,
            width=width if width else None,
            distance=min_distance,
        )

        for i, pk in enumerate(peaks):
            all_dips.append(
                {
                    "Cycle": cycle_idx,
                    "Relative_Time": rel_time[pk],
                    "CH2_Depth": props["prominences"][i],
                    "CH3_Voltage": ch3_seg[pk],
                }
            )

    if not all_dips:
        return pd.DataFrame(
            columns=["Cycle", "Relative_Time", "CH2_Depth", "CH3_Voltage", "Group"]
        )

    # ---- Cluster dips across cycles by relative-time proximity ----
    dips_sorted = sorted(all_dips, key=lambda d: d["Relative_Time"])

    group_id = 0
    dips_sorted[0]["Group"] = group_id
    for i in range(1, len(dips_sorted)):
        if (
            dips_sorted[i]["Relative_Time"] - dips_sorted[i - 1]["Relative_Time"]
            > cluster_threshold
        ):
            group_id += 1
        dips_sorted[i]["Group"] = group_id

    return pd.DataFrame(dips_sorted)
