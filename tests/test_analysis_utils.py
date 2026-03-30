from uncertainties import ufloat

from src.analysis.fitting import excel_style_regression_with_propagation
from src.analysis.formatting import ufloat_to_paren


def test_ufloat_to_paren_formats_two_significant_digits() -> None:
    assert ufloat_to_paren(ufloat(1.34836, 0.00043)) == "1.34836(43)"
    assert ufloat_to_paren(ufloat(12.345, 0.067)) == "12.345(67)"
    assert ufloat_to_paren(ufloat(0.1234, 0.0012)) == "0.1234(12)"


def test_excel_style_regression_accepts_scalar_uncertainties() -> None:
    slope, intercept = excel_style_regression_with_propagation(
        x=[0, 1, 2, 3],
        y=[1, 3, 5, 7],
        sigma_x=0.01,
        sigma_y=0.02,
    )

    assert abs(slope.n - 2.0) < 1e-12
    assert abs(intercept.n - 1.0) < 1e-12
    assert slope.s > 0
    assert intercept.s > 0
