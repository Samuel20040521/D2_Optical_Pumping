from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from src.visualization import create_figure, save_figure


def test_create_figure_applies_labels_and_size() -> None:
    fig, ax = create_figure(
        xlabel="Distance [mm]",
        ylabel="Time [us]",
        figsize=(7.0, 5.0),
    )

    assert ax.get_xlabel() == "Distance [mm]"
    assert ax.get_ylabel() == "Time [us]"
    assert tuple(round(v, 1) for v in fig.get_size_inches()) == (7.0, 5.0)

    plt.close(fig)


def test_save_figure_writes_file(tmp_path: Path) -> None:
    fig, ax = create_figure(xlabel="x", ylabel="y")
    ax.plot([0, 1], [0, 1])

    output_path = save_figure(fig, "demo.pdf", directory=tmp_path, close=True)

    assert output_path == tmp_path / "demo.pdf"
    assert output_path.exists()
