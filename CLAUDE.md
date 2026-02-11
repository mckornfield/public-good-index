# Project: Public Good Index (PGI) Calculator

## Overview
Calculates a Public Good Index for US states and top 100 cities, combining tax burden, spending allocation (investment vs cost), and service effectiveness into a single 0-100 score.

## Architecture
- `src/data_utils.py` — State-level data loading: Census tax collections, BEA personal income, population, RPP/COL weights, SSA payments, NAEP scores, FBI crime, CDC infant mortality
- `src/city_data_utils.py` — City-level data loading: top 100 cities, tax revenue, spending, crime, education, health, city COL weights
- `notebooks/` — Jupyter notebooks (01-08) that produce analysis outputs

## Notebook Pipeline
Notebooks must run in order (later ones depend on CSVs from earlier ones):
1. `01_tax_burden` — State tax burden rates and per-capita taxes
2. `02_spending_allocation` — State spending breakdown (investment vs cost)
3. `03_service_effectiveness` — State outcome metrics (education, crime, health)
4. `04_public_good_score` — Combines 01-03 into state PGI (depends on all 3 CSVs)
5. `05_city_tax_burden` — City tax per capita
6. `06_city_spending` — City spending breakdown
7. `07_city_effectiveness` — City outcome metrics
8. `08_city_public_good` — Combines 05-07 into city PGI (depends on all 3 CSVs)

## Cost-of-Living Normalization
All dollar-denominated metrics have COL-adjusted variants using BEA Regional Price Parities (RPP):
- `col_weight = min(RPP) / state_RPP` — cheapest state (Arkansas, RPP=86.5) gets weight=1.0
- `adj_*` columns = raw value * col_weight
- State RPP data: `_RPP_2023` dict in `data_utils.py`, `get_col_weights()` function
- City COL: `get_city_col_weights()` in `city_data_utils.py` (inherits parent state RPP)
- PGI notebooks (04, 08) include an alternative COL-adjusted PGI using adj_investment_per_capita

## Running Notebooks
```bash
.venv/bin/python -m papermill notebooks/01_tax_burden.ipynb /dev/null --cwd notebooks
```
Note: Notebook 02 can take ~1 min due to Census download attempts that 404.

## Generating the HTML Report
After running notebooks, regenerate `docs/report.html` from their outputs:
```bash
.venv/bin/python scripts/generate_html.py
```
This extracts all cell outputs (text, images, Plotly charts) into a single standalone HTML file.

## Data Outputs
- `data/processed/` — CSV files consumed by downstream notebooks and exports
- `docs/charts/data/` — JSON files for D3 web visualizations

## Environment
- Python 3.9 virtualenv at `.venv/`
- Requires `BEA_API_KEY` in `.env` for notebook 01
- Key dependencies: pandas, numpy, matplotlib, plotly, scipy, papermill
