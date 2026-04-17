from __future__ import annotations

import numpy as np
from uncertainties import ufloat
from scipy.optimize import least_squares


def nonlinear_regression_with_propagation(
    model_func,
    x,
    y,
    sigma_x,
    sigma_y,
    p0,
    param_names=None,
    bounds=(-np.inf, np.inf),
):
    """
    Perform nonlinear regression and propagate x/y uncertainties to the fit
    parameters using analytic (numerical) gradient propagation.

    This generalises ``excel_style_regression_with_propagation`` to arbitrary
    nonlinear models while keeping the same philosophy:

        1. Obtain best-fit parameters via ordinary least-squares
           (ignoring uncertainties in the minimisation itself).
        2. Propagate measurement uncertainties (σ_x, σ_y) to the fitted
           parameters analytically through the implicit-function theorem.

    Parameters
    ----------
    model_func : callable
        ``model_func(x, *params) -> y_pred``.  Must be vectorised in *x*.
    x, y : array-like
        Measured data.
    sigma_x, sigma_y : float or array-like
        Per-point measurement uncertainties.
    p0 : array-like
        Initial parameter guess.
    param_names : list[str] or None
        Optional human-readable names for the parameters.
    bounds : 2-tuple of array-like
        Lower and upper bounds forwarded to ``scipy.optimize.least_squares``.

    Returns
    -------
    dict  with keys
        ``params``      – list of ``ufloat`` (value ± propagated uncertainty)
        ``param_names`` – list of str
        ``residuals``   – array of residuals at the best-fit
        ``popt``        – raw best-fit parameter array
        ``cov_prop``    – full propagated covariance matrix of parameters

    Theory
    ------
    At the best-fit the parameters satisfy the normal equations

        ∂χ²/∂pₖ = -2 Σᵢ rᵢ ∂fᵢ/∂pₖ = 0          … (*)

    where rᵢ = yᵢ - f(xᵢ, p) and f is the model.

    Each data point (xᵢ, yᵢ) contributes to (*); small shifts δxᵢ or δyᵢ
    produce shifts δpₖ in the solution.  The implicit-function theorem gives

        δpₖ = Σᵢ [ (∂pₖ/∂yᵢ) δyᵢ  +  (∂pₖ/∂xᵢ) δxᵢ ]

    where the Jacobians ∂p/∂y and ∂p/∂x are obtained by differentiating (*)
    with respect to yᵢ and xᵢ.  We compute these numerically with finite
    differences (just like numpy.gradient) — this avoids having to derive
    analytic gradients for every new model.

    The propagated covariance of p is then

        Cov(p) = (∂p/∂y) diag(σ_y²) (∂p/∂y)ᵀ
               + (∂p/∂x) diag(σ_x²) (∂p/∂x)ᵀ

    which is the direct generalisation of the formula used in
    ``excel_style_regression_with_propagation``.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    p0 = np.asarray(p0, dtype=float)
    n = len(x)
    n_params = len(p0)

    if np.isscalar(sigma_x):
        sigma_x = np.full(n, float(sigma_x))
    else:
        sigma_x = np.asarray(sigma_x, dtype=float)
    if np.isscalar(sigma_y):
        sigma_y = np.full(n, float(sigma_y))
    else:
        sigma_y = np.asarray(sigma_y, dtype=float)

    if param_names is None:
        param_names = [f"p{i}" for i in range(n_params)]

    # ── Step 1: ordinary least-squares fit ──────────────────────────
    def residuals(p):
        return y - model_func(x, *p)

    result = least_squares(residuals, p0, bounds=bounds)
    popt = result.x.copy()

    # ── Step 2: numerical Jacobians ∂p/∂y  and  ∂p/∂x ──────────────
    #
    # Strategy: perturb each yᵢ (or xᵢ) by a tiny amount, re-solve,
    # and record how popt shifts.  This is the most robust approach
    # for an arbitrary model.
    #
    # For speed we use a single-step forward difference. The step size
    # is chosen relative to the data scale.

    dp_dy = np.zeros((n_params, n))  # ∂pₖ/∂yᵢ
    dp_dx = np.zeros((n_params, n))  # ∂pₖ/∂xᵢ

    y_scale = np.std(y) if np.std(y) > 0 else 1.0
    x_scale = np.std(x) if np.std(x) > 0 else 1.0
    eps_y = y_scale * 1e-6
    eps_x = x_scale * 1e-6

    for i in range(n):
        # ── perturb yᵢ ──
        y_pert = y.copy()
        y_pert[i] += eps_y

        def res_y(p):
            return y_pert - model_func(x, *p)

        sol = least_squares(res_y, popt, bounds=bounds)
        dp_dy[:, i] = (sol.x - popt) / eps_y

        # ── perturb xᵢ ──
        x_pert = x.copy()
        x_pert[i] += eps_x

        def res_x(p):
            return y - model_func(x_pert, *p)

        sol = least_squares(res_x, popt, bounds=bounds)
        dp_dx[:, i] = (sol.x - popt) / eps_x

    # ── Step 3: propagated covariance ───────────────────────────────
    cov_y = dp_dy @ np.diag(sigma_y**2) @ dp_dy.T
    cov_x = dp_dx @ np.diag(sigma_x**2) @ dp_dx.T
    cov_prop = cov_y + cov_x

    param_std = np.sqrt(np.diag(cov_prop))

    params_ufloat = [ufloat(popt[k], param_std[k]) for k in range(n_params)]

    return {
        "params": params_ufloat,
        "param_names": param_names,
        "residuals": residuals(popt),
        "popt": popt,
        "cov_prop": cov_prop,
    }


# ── Convenience wrapper for T = a/V + b ────────────────────────────


def inverse_linear_regression_with_propagation(V, T, sigma_V, sigma_T):
    """
    Fit ``T = a / V + b`` propagating both voltage and period uncertainties.

    This is a direct analogue of ``excel_style_regression_with_propagation``
    for the inverse-proportional model used in the ringing-period analysis.

    Returns
    -------
    a, b : ufloat
        Fitted parameters with propagated uncertainties.
    result : dict
        Full result dict from ``nonlinear_regression_with_propagation``.
    """

    def model(v, a, b):
        return a / v + b

    # sensible initial guesses
    V = np.asarray(V, dtype=float)
    T = np.asarray(T, dtype=float)
    a0 = (T[0] - T[-1]) * V[0] * V[-1] / (V[-1] - V[0])
    b0 = T[-1] - a0 / V[-1]

    result = nonlinear_regression_with_propagation(
        model_func=model,
        x=V,
        y=T,
        sigma_x=sigma_V,
        sigma_y=sigma_T,
        p0=[a0, b0],
        param_names=["a", "b"],
    )

    a_uf, b_uf = result["params"]
    return a_uf, b_uf, result


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
        x_variance_term * (y - ybar) - (xybar - xbar * ybar) * (2 * x - 2 * xbar)
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
