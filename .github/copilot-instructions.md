# Copilot Instructions for Modern Physics Experiment Data Analysis

## Project Purpose

This repository is a reusable template for laboratory data analysis projects.

The expected workflow is:

1. keep raw data immutable,
2. clean and validate data with explicit code,
3. perform uncertainty-aware analysis,
4. generate report-ready figures and tables.

## Repository Conventions

- Treat `data/raw/` as read-only input.
- Put reusable logic in `src/`, not only in notebooks.
- Save intermediate outputs in `data/interim/`.
- Save final analysis-ready datasets in `data/processed/`.
- Save report artifacts in `reports/figures/` and `reports/tables/`.

## Preferred Folder Usage

- `src/io/`: data loading and parsing
- `src/preprocessing/`: cleaning and reshaping
- `src/uncertainty/`: uncertainty propagation and budgets
- `src/analysis/`: fitting, regression, derived quantities
- `src/visualization/`: plotting and styling

## Python Tooling

- Use `uv` for environment and dependency management.
- Prefer `uv sync`, `uv add`, and `uv run ...`.
- Update `pyproject.toml` when adding dependencies.

## Coding Guidance

- Keep raw data untouched.
- Make transformation steps explicit and reproducible.
- Separate file I/O, preprocessing, analysis, and visualization.
- Favor small reusable functions over notebook-only logic.
