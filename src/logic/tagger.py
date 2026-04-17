"""
Assign physical labels to aggregated dip groups based on the
experimental category derived from the filename.

Tagging rules
-------------
Category 1 (B0 baseline):
    Deepest dip -> "B0"; everything else -> "invalid".

Category 2 (low-field RF, freq <= 200 kHz):
    Deepest dip -> "B0";
    Next dip in time after B0 -> "Rb-85";
    Following dip -> "Rb-87";
    Dips before B0 -> "invalid".

Category 3 (high-field / MAIN, freq > 200 kHz):
    Deepest dip -> "Rb-85";
    Next dip in time -> "Rb-87";
    Dips before Rb-85 -> "invalid".
"""

import pandas as pd


def assign_tags(dips_df: pd.DataFrame, category: int) -> pd.DataFrame:
    """
    Label each aggregated dip group with a physical tag.

    Parameters
    ----------
    dips_df : pd.DataFrame
        Aggregated dip table **sorted by** ``Relative_Time``.
        Must contain at least ``Relative_Time`` and ``CH2_Depth``.
    category : int
        Experimental category (1, 2, or 3) from ``parse_metadata``.

    Returns
    -------
    pd.DataFrame
        A copy of *dips_df* with an added ``tag`` column whose values
        are one of ``"B0"``, ``"Rb-85"``, ``"Rb-87"``, ``"invalid"``,
        or ``"unknown"``.
    """
    df = dips_df.sort_values("Relative_Time").reset_index(drop=True)
    df["tag"] = "unknown"

    if len(df) == 0:
        return df

    # Index of the deepest dip (largest prominence value)
    deepest = df["CH2_Depth"].idxmax()

    if category == 1:
        df.loc[deepest, "tag"] = "B0"
        df.loc[df.index != deepest, "tag"] = "invalid"

    elif category == 2:
        df.loc[deepest, "tag"] = "B0"
        # Everything before B0 in time is invalid
        df.loc[df.index < deepest, "tag"] = "invalid"
        # Tag the first two dips after B0
        after = df.index[df.index > deepest]
        if len(after) >= 1:
            df.loc[after[0], "tag"] = "Rb-85"
        if len(after) >= 2:
            df.loc[after[1], "tag"] = "Rb-87"

    elif category == 3:
        df.loc[deepest, "tag"] = "Rb-85"
        # Everything before Rb-85 in time is invalid
        df.loc[df.index < deepest, "tag"] = "invalid"
        # Tag the next dip after Rb-85
        after = df.index[df.index > deepest]
        if len(after) >= 1:
            df.loc[after[0], "tag"] = "Rb-87"

    return df
