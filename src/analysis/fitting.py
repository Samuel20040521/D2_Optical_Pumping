from __future__ import annotations

import numpy as np
from uncertainties import ufloat


def excel_style_regression_with_propagation(x, y, sigma_x, sigma_y):
    """
    Perform a linear regression and propagate x/y uncertainties to the fit.

    This mirrors the spreadsheet-style workflow used in many laboratory courses:
    first compute the ordinary least-squares slope and intercept, then propagate
    measurement uncertainties to the fitted parameters analytically.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    if np.isscalar(sigma_x):
        sigma_x = np.full_like(x, float(sigma_x), dtype=float)
    else:
        sigma_x = np.asarray(sigma_x, dtype=float)

    if np.isscalar(sigma_y):
        sigma_y = np.full_like(y, float(sigma_y), dtype=float)
    else:
        sigma_y = np.asarray(sigma_y, dtype=float)

    n = len(x)
    if len(y) != n:
        raise ValueError("x and y must have the same length")
    if len(sigma_x) != n or len(sigma_y) != n:
        raise ValueError("sigma_x and sigma_y must match the data length")
    if n < 2:
        raise ValueError("need at least two points")

    xbar = np.mean(x)
    x2bar = np.mean(x**2)
    ybar = np.mean(y)
    xybar = np.mean(x * y)

    x_variance_term = x2bar - xbar**2
    if np.isclose(x_variance_term, 0.0):
        raise ValueError("x values are identical, cannot fit a line")

    slope_value = (xybar - xbar * ybar) / x_variance_term
    intercept_value = ybar - slope_value * xbar

    slope_grad_x = (
        x_variance_term * (y - ybar)
        - (xybar - xbar * ybar) * (2 * x - 2 * xbar)
    ) / (n * x_variance_term**2)
    slope_grad_y = (x - xbar) / (n * x_variance_term)

    slope_std = np.sqrt(
        np.sum((slope_grad_x * sigma_x) ** 2) + np.sum((slope_grad_y * sigma_y) ** 2)
    )

    intercept_grad_x = -(slope_grad_x * xbar + slope_value / n)
    intercept_grad_y = 1 / n - slope_grad_y * xbar

    intercept_std = np.sqrt(
        np.sum((intercept_grad_x * sigma_x) ** 2)
        + np.sum((intercept_grad_y * sigma_y) ** 2)
    )

    return ufloat(slope_value, slope_std), ufloat(intercept_value, intercept_std)
