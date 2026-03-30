from __future__ import annotations

import math


def ufloat_to_paren(x, scientific: bool = False) -> str:
    """
    Format an uncertainties value using the standard physics parenthesis notation.

    Examples:
        1.34836 +/- 0.00043 -> 1.34836(43)
        12.345 +/- 0.067 -> 12.345(67)
    """
    val = x.n
    err = x.s

    if err == 0:
        return f"{val:g}" if scientific else f"{val}"

    magnitude = math.floor(math.log10(abs(err)))
    significant_digits = 2
    rounding_place = magnitude - (significant_digits - 1)

    err_rounded = round(err, -rounding_place)

    if abs(err_rounded) >= 10 ** (magnitude + 1):
        magnitude += 1
        rounding_place = magnitude - (significant_digits - 1)
        err_rounded = round(err, -rounding_place)

    val_rounded = round(val, -rounding_place)

    if scientific:
        if val_rounded != 0:
            val_magnitude = math.floor(math.log10(abs(val_rounded)))
        else:
            val_magnitude = 0

        val_shifted = val_rounded / (10**val_magnitude)
        err_shifted = err_rounded / (10**val_magnitude)

        new_rounding_place = rounding_place - val_magnitude
        decimals = max(0, -new_rounding_place)

        val_str = f"{val_shifted:.{decimals}f}"
        err_digits = round(err_shifted * 10**decimals)
        return f"{val_str}({err_digits})e{val_magnitude}"

    decimals = max(0, -rounding_place)
    val_str = f"{val_rounded:.{decimals}f}"

    if rounding_place < 0:
        err_digits = round(err_rounded * 10**decimals)
    else:
        err_digits = round(err_rounded)

    return f"{val_str}({err_digits})"
