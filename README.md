# Public Good Index

Measuring how effectively each US state converts tax dollars into public good.

## What does this measure?

The **Public Good Index** scores each state on a 0–100 scale, where 100 means tax dollars are being used highly effectively for the public good, and 0 means taxpayers are getting almost nothing back.

A low score means: high tax burden, low investment in the community, and low effectiveness of services.

Inspired by the [Corruption Perceptions Index](https://en.wikipedia.org/wiki/Corruption_Perceptions_Index) methodology — we normalize each sub-metric to a 0–100 scale using z-scores, then aggregate via simple average.

## Criteria

### 1. Tax Burden
Total tax burden on individuals, including:
- State income tax
- Property tax
- Sales tax
- State fees
- Federal payroll taxes: Social Security (FICA), Medicare, FMLA/paid family leave

### 2. Service Allocation
Where tax revenue is spent, classified as:

**Investment** (produces future economic returns):
- K-12 education
- Higher education
- Children's health programs (CHIP)
- Childcare / family leave programs (FMLA, state PFML)
- Infrastructure / highways
- Public safety

**Cost** (necessary but purely consumptive):
- Social Security
- Elderly care / nursing facilities
- Medicaid (elderly portion)
- Pensions

### 3. Service Effectiveness
How well services actually improve quality of life:
- Education outcomes (NAEP scores, graduation rates)
- Infrastructure quality (ASCE grades, road conditions)
- Public safety (crime rates)
- Child health outcomes

### 4. Economic Value Creation
The ratio of investment spending to total spending. Investment spending produces future taxpayers and economic activity; cost spending is necessary but doesn't generate returns.

## Scoring

Each sub-metric is normalized to 0–100 using z-score standardization (matching the CPI approach):
1. Calculate z-score: `z = (value - mean) / std_dev`
2. Rescale to 0–100 range
3. Final score = average of normalized sub-scores

```
public_good = f(tax_efficiency, investment_ratio, effectiveness)
```

Where high tax burden with low investment and low effectiveness = low public good score.

## Project Structure

```
├── data/
│   ├── raw/           # Original downloaded datasets
│   └── processed/     # Cleaned and merged data
├── notebooks/         # Jupyter notebooks for analysis
├── src/               # Python modules for data fetching and processing
└── docs/
    └── charts/        # D3 visualizations for GitHub Pages
```

## Data Sources

- [Census Bureau - State Tax Collections](https://www.census.gov/programs-surveys/stc.html)
- [Census Annual Survey of State Government Finances](https://www.census.gov/programs-surveys/state.html)
- [NAEP - National Assessment of Educational Progress](https://nces.ed.gov/nationsreportcard/)
- [FBI Uniform Crime Reporting](https://www.fbi.gov/how-we-can-help-you/more-fbi-services-and-information/ucr)
- [ASCE Infrastructure Report Card](https://infrastructurereportcard.org/)
- [SSA - Social Security Administration](https://www.ssa.gov/policy/docs/statcomps/)
- [DOL - Family and Medical Leave](https://www.dol.gov/agencies/whd/fmla)

## Visualization

Charts are built with D3.js and published via GitHub Pages at the `docs/` directory.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
