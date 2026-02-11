"""Shared data-loading utilities for the Public Good Index project."""

import os
from pathlib import Path

import pandas as pd
import requests


def download_file(url: str, dest: Path, *, force: bool = False) -> Path:
    """Download a file from *url* and save it to *dest*.

    Skips the download if *dest* already exists unless *force* is True.
    Creates parent directories as needed.
    """
    dest = Path(dest)
    if dest.exists() and not force:
        print(f"Already downloaded: {dest}")
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url} …")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    print(f"Saved to {dest} ({len(resp.content):,} bytes)")
    return dest


def load_census_stc(path: Path) -> pd.DataFrame:
    """Parse the Census STC transposed Excel file into a tidy DataFrame.

    Returns a DataFrame with columns:
        state       – two-letter abbreviation (e.g. "CA")
        state_name  – full name (e.g. "California")
        category    – tax category (e.g. "Total Taxes")
        amount      – dollar amount (thousands)
    """
    # The transposed STC file has states as columns and tax categories as rows.
    # Row 0 is typically the header row with state names.
    xls = pd.read_excel(path, header=None)

    # --- Locate the header row (contains "United States" or state names) ------
    header_row = None
    for i, row in xls.iterrows():
        if row.astype(str).str.contains("United States", case=False).any():
            header_row = i
            break
    if header_row is None:
        raise ValueError("Could not locate header row in STC spreadsheet")

    # Re-read with the correct header
    df = pd.read_excel(path, header=header_row)

    # First column is the tax category label
    cat_col = df.columns[0]
    df = df.rename(columns={cat_col: "category"})

    # Drop any fully-empty rows
    df = df.dropna(subset=["category"])

    # Melt from wide to long: one row per (category, state)
    id_vars = ["category"]
    value_vars = [c for c in df.columns if c not in id_vars]
    long = df.melt(id_vars=id_vars, value_vars=value_vars,
                   var_name="state_name", value_name="amount")

    # Coerce amount to numeric (some cells may be "X" or "-")
    long["amount"] = pd.to_numeric(long["amount"], errors="coerce")

    # Build a state abbreviation lookup
    long["state"] = long["state_name"].map(_state_name_to_abbr())

    # Drop rows we can't map (footnotes, aggregates like "United States")
    long = long.dropna(subset=["state"]).reset_index(drop=True)

    return long[["state", "state_name", "category", "amount"]]


def fetch_bea_personal_income(api_key: str, year: str = "2023") -> pd.DataFrame:
    """Fetch state personal income from the BEA Regional API.

    Returns a DataFrame with columns: state, state_name, personal_income.
    """
    url = "https://apps.bea.gov/api/data"
    params = {
        "UserID": api_key,
        "method": "GetData",
        "datasetname": "Regional",
        "TableName": "SAINC1",
        "LineCode": "1",
        "GeoFIPS": "STATE",
        "Year": year,
        "ResultFormat": "JSON",
    }
    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    results = data["BEAAPI"]["Results"]["Data"]
    rows = []
    for r in results:
        geo = r.get("GeoName", "")
        fips = r.get("GeoFips", "")
        val = r.get("DataValue", "")
        if fips in ("00000",):  # skip US total
            continue
        # BEA values are in thousands of dollars (or plain dollars depending
        # on table).  SAINC1 Line 1 is in thousands.
        try:
            val = float(str(val).replace(",", ""))
        except ValueError:
            continue
        rows.append({"state_name": geo, "personal_income": val})

    df = pd.DataFrame(rows)
    df["state"] = df["state_name"].map(_state_name_to_abbr())
    df = df.dropna(subset=["state"]).reset_index(drop=True)
    return df[["state", "state_name", "personal_income"]]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _state_name_to_abbr() -> dict:
    """Return a dict mapping full state name → two-letter abbreviation."""
    return {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
        "California": "CA", "Colorado": "CO", "Connecticut": "CT",
        "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
        "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
        "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME",
        "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
        "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
        "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
        "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
        "New York": "NY", "North Carolina": "NC", "North Dakota": "ND",
        "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
        "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
        "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
        "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
        "Wisconsin": "WI", "Wyoming": "WY",
        "District of Columbia": "DC",
    }


# ---------------------------------------------------------------------------
# State Population Data
# ---------------------------------------------------------------------------

# 2023 Census population estimates (July 1, 2023)
_STATE_POPULATION_FALLBACK = {
    "AL": 5108468, "AK": 733406, "AZ": 7431344, "AR": 3067732,
    "CA": 38965193, "CO": 5877610, "CT": 3617176, "DE": 1031890,
    "FL": 22610726, "GA": 11029227, "HI": 1435138, "ID": 1964726,
    "IL": 12549689, "IN": 6862199, "IA": 3207004, "KS": 2940546,
    "KY": 4526154, "LA": 4573749, "ME": 1395722, "MD": 6180253,
    "MA": 7001399, "MI": 10037261, "MN": 5737915, "MS": 2939690,
    "MO": 6196156, "MT": 1132812, "NE": 1978379, "NV": 3194176,
    "NH": 1402054, "NJ": 9290841, "NM": 2114371, "NY": 19571216,
    "NC": 10835491, "ND": 783926, "OH": 11785935, "OK": 4053824,
    "OR": 4233358, "PA": 12961683, "RI": 1095962, "SC": 5373555,
    "SD": 919318, "TN": 7126489, "TX": 30503301, "UT": 3417734,
    "VT": 647464, "VA": 8642274, "WA": 7812880, "WV": 1770071,
    "WI": 5910955, "WY": 584057, "DC": 678972,
}


def fetch_state_population(year: str = "2023") -> pd.DataFrame:
    """Fetch state population estimates.

    Returns a DataFrame with columns: state, state_name, population.
    """
    abbr_to_name = {v: k for k, v in _state_name_to_abbr().items()}

    # Fallback to embedded data (Census 2023 estimates)
    print("Using embedded Census 2023 population data")
    rows = []
    for abbr, pop in _STATE_POPULATION_FALLBACK.items():
        rows.append({
            "state": abbr,
            "state_name": abbr_to_name.get(abbr, abbr),
            "population": pop,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# BEA Regional Price Parities (RPP) — Cost-of-Living Normalization
# ---------------------------------------------------------------------------

# 2023 BEA Regional Price Parities (all items, states + DC)
# National average = 100.  Source: FRED / BEA PARPP table.
_RPP_2023 = {
    "AL": 87.8, "AK": 105.4, "AZ": 97.8, "AR": 86.5, "CA": 112.6,
    "CO": 104.3, "CT": 108.7, "DE": 100.0, "FL": 100.6, "GA": 92.3,
    "HI": 119.2, "ID": 95.2, "IL": 97.0, "IN": 90.7, "IA": 89.5,
    "KS": 90.3, "KY": 89.0, "LA": 90.0, "ME": 99.3, "MD": 109.7,
    "MA": 110.1, "MI": 91.9, "MN": 98.0, "MS": 86.7, "MO": 88.8,
    "MT": 95.5, "NE": 91.5, "NV": 98.0, "NH": 106.0, "NJ": 113.5,
    "NM": 92.8, "NY": 115.9, "NC": 93.1, "ND": 91.2, "OH": 90.4,
    "OK": 88.4, "OR": 100.9, "PA": 97.5, "RI": 100.3, "SC": 91.1,
    "SD": 90.6, "TN": 91.2, "TX": 95.3, "UT": 97.9, "VT": 103.2,
    "VA": 103.4, "WA": 107.5, "WV": 86.7, "WI": 93.5, "WY": 95.3,
    "DC": 116.8,
}


def get_col_weights() -> pd.DataFrame:
    """Return a DataFrame with cost-of-living weights for each state.

    Columns: state, rpp, col_weight
    col_weight = min(RPP) / state_RPP  →  cheapest state gets 1.0,
    expensive states get < 1.0.
    """
    min_rpp = min(_RPP_2023.values())
    rows = []
    for st, rpp in _RPP_2023.items():
        rows.append({"state": st, "rpp": rpp, "col_weight": min_rpp / rpp})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Census State Government Finances
# ---------------------------------------------------------------------------

def load_census_state_finances(path: Path) -> pd.DataFrame:
    """Parse Census Annual Survey of State Government Finances Excel file.

    Returns a DataFrame with columns:
        state       – two-letter abbreviation
        state_name  – full name
        category    – spending category
        amount      – dollar amount (thousands)
    """
    xls = pd.read_excel(path, header=None)

    # Locate the header row (contains "United States" or state names)
    header_row = None
    for i, row in xls.iterrows():
        if row.astype(str).str.contains("United States", case=False).any():
            header_row = i
            break
    if header_row is None:
        raise ValueError("Could not locate header row in state finances spreadsheet")

    df = pd.read_excel(path, header=header_row)

    cat_col = df.columns[0]
    df = df.rename(columns={cat_col: "category"})
    df = df.dropna(subset=["category"])

    id_vars = ["category"]
    value_vars = [c for c in df.columns if c not in id_vars]
    long = df.melt(id_vars=id_vars, value_vars=value_vars,
                   var_name="state_name", value_name="amount")

    long["amount"] = pd.to_numeric(long["amount"], errors="coerce")
    long["state"] = long["state_name"].map(_state_name_to_abbr())
    long = long.dropna(subset=["state"]).reset_index(drop=True)

    return long[["state", "state_name", "category", "amount"]]


def load_asfin_state_finances(path: Path) -> pd.DataFrame:
    """Parse the Census ASFIN State Totals Excel file (expenditure by function).

    The ASFIN file has a wide layout: categories as rows, states as columns.
    We extract the 'General expenditure, by function' section which contains:
    Education, Public welfare, Hospitals, Health, Highways, Police protection,
    Correction, Natural resources, Parks and recreation, Governmental
    administration, Interest on general debt, Other and unallocable.

    Returns a DataFrame with columns:
        state       – two-letter abbreviation
        state_name  – full name
        category    – spending function name (stripped)
        amount      – dollar amount (thousands)
    """
    xls = pd.read_excel(path, header=None)

    # Find the header row (contains "United States")
    header_row = None
    for i, row in xls.iterrows():
        if row.astype(str).str.contains("United States", case=False).any():
            header_row = i
            break
    if header_row is None:
        raise ValueError("Could not locate header row in ASFIN spreadsheet")

    df = pd.read_excel(path, header=header_row)
    cat_col = df.columns[0]
    df = df.rename(columns={cat_col: "category"})

    # Find the expenditure-by-function section
    # Look for rows between "General expenditure, by function:" and "Utility expenditure"
    cat_values = df["category"].astype(str).tolist()
    start_idx = None
    end_idx = None
    for i, val in enumerate(cat_values):
        if "by function" in val.lower():
            start_idx = i + 1
        elif start_idx is not None and ("utility expenditure" in val.lower()
                                         or "liquor stores" in val.lower()):
            end_idx = i
            break

    if start_idx is None:
        raise ValueError("Could not find 'General expenditure, by function' section")
    if end_idx is None:
        end_idx = len(cat_values)

    # Extract just the function rows
    func_df = df.iloc[start_idx:end_idx].copy()
    func_df = func_df.dropna(subset=["category"])
    # Strip whitespace from category names
    func_df["category"] = func_df["category"].str.strip()
    # Drop empty category rows
    func_df = func_df[func_df["category"].str.len() > 0]

    # Melt to long format
    value_vars = [c for c in func_df.columns if c != "category"]
    long = func_df.melt(id_vars=["category"], value_vars=value_vars,
                        var_name="state_name", value_name="amount")

    long["amount"] = pd.to_numeric(long["amount"], errors="coerce")
    long["state"] = long["state_name"].map(_state_name_to_abbr())
    long = long.dropna(subset=["state"]).reset_index(drop=True)

    return long[["state", "state_name", "category", "amount"]]


# ---------------------------------------------------------------------------
# SSA OASDI Benefit Payments
# ---------------------------------------------------------------------------

_SSA_OASDI_FALLBACK = {
    "AL": 14063, "AK": 1394, "AZ": 17892, "AR": 8784, "CA": 78670,
    "CO": 12160, "CT": 9390, "DE": 2683, "FL": 58702, "GA": 23340,
    "HI": 3442, "ID": 4736, "IL": 29544, "IN": 17016, "IA": 8466,
    "KS": 7068, "KY": 12222, "LA": 11736, "ME": 4056, "MD": 13722,
    "MA": 16056, "MI": 27102, "MN": 13440, "MS": 8484, "MO": 16188,
    "MT": 2928, "NE": 4788, "NV": 7416, "NH": 3756, "NJ": 22212,
    "NM": 5292, "NY": 47388, "NC": 25560, "ND": 1752, "OH": 30078,
    "OK": 10008, "OR": 11202, "PA": 35100, "RI": 2892, "SC": 14298,
    "SD": 2376, "TN": 17988, "TX": 54750, "UT": 5544, "VT": 1782,
    "VA": 19260, "WA": 17040, "WV": 5916, "WI": 15114, "WY": 1434,
    "DC": 1020,
}


def fetch_ssa_oasdi_payments() -> pd.DataFrame:
    """Fetch OASDI benefit payments by state from SSA.

    Returns a DataFrame with columns: state, state_name, total_benefits
    (total_benefits in millions of dollars).
    """
    url = "https://www.ssa.gov/OACT/ProgData/funds/data/OASDIBenefitPaymentsByState.csv"
    abbr_to_name = {v: k for k, v in _state_name_to_abbr().items()}

    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        lines = resp.text.strip().splitlines()

        # Try to parse as CSV
        from io import StringIO
        raw = pd.read_csv(StringIO(resp.text))

        # Expect columns like: State, Total Benefits (or similar)
        raw.columns = [c.strip() for c in raw.columns]
        state_col = [c for c in raw.columns if "state" in c.lower()]
        benefit_col = [c for c in raw.columns if "total" in c.lower() or "benefit" in c.lower()]

        if state_col and benefit_col:
            df = raw[[state_col[0], benefit_col[0]]].copy()
            df.columns = ["state_name", "total_benefits"]
            df["total_benefits"] = pd.to_numeric(
                df["total_benefits"].astype(str).str.replace(",", ""), errors="coerce"
            )
            df["state"] = df["state_name"].map(_state_name_to_abbr())
            df = df.dropna(subset=["state", "total_benefits"]).reset_index(drop=True)
            if len(df) >= 40:
                return df[["state", "state_name", "total_benefits"]]
    except Exception:
        pass

    # Fallback to embedded data
    print("Using embedded SSA OASDI data (fallback)")
    rows = []
    for abbr, amount in _SSA_OASDI_FALLBACK.items():
        rows.append({
            "state": abbr,
            "state_name": abbr_to_name.get(abbr, abbr),
            "total_benefits": float(amount),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# NAEP Test Scores
# ---------------------------------------------------------------------------

_NAEP_MATH_FALLBACK = {
    "AL": 267, "AK": 272, "AZ": 278, "AR": 273, "CA": 276,
    "CO": 283, "CT": 282, "DE": 276, "FL": 280, "GA": 276,
    "HI": 274, "ID": 284, "IL": 278, "IN": 283, "IA": 284,
    "KS": 284, "KY": 278, "LA": 268, "ME": 282, "MD": 278,
    "MA": 292, "MI": 274, "MN": 288, "MS": 265, "MO": 279,
    "MT": 286, "NE": 284, "NV": 274, "NH": 288, "NJ": 288,
    "NM": 265, "NY": 276, "NC": 279, "ND": 286, "OH": 281,
    "OK": 271, "OR": 280, "PA": 282, "RI": 275, "SC": 275,
    "SD": 284, "TN": 274, "TX": 279, "UT": 284, "VT": 286,
    "VA": 284, "WA": 283, "WV": 268, "WI": 284, "WY": 284,
    "DC": 263,
}

_NAEP_READING_FALLBACK = {
    "AL": 252, "AK": 256, "AZ": 260, "AR": 256, "CA": 260,
    "CO": 267, "CT": 267, "DE": 261, "FL": 264, "GA": 261,
    "HI": 258, "ID": 264, "IL": 263, "IN": 265, "IA": 266,
    "KS": 266, "KY": 262, "LA": 252, "ME": 268, "MD": 263,
    "MA": 274, "MI": 260, "MN": 270, "MS": 249, "MO": 264,
    "MT": 269, "NE": 267, "NV": 258, "NH": 271, "NJ": 271,
    "NM": 252, "NY": 260, "NC": 263, "ND": 268, "OH": 266,
    "OK": 257, "OR": 264, "PA": 267, "RI": 259, "SC": 259,
    "SD": 266, "TN": 260, "TX": 262, "UT": 266, "VT": 270,
    "VA": 267, "WA": 266, "WV": 254, "WI": 266, "WY": 267,
    "DC": 246,
}


def fetch_naep_scores(subject: str = "mathematics", grade: int = 8) -> pd.DataFrame:
    """Fetch NAEP test scores by state from the Nations Report Card API.

    Returns a DataFrame with columns: state, state_name, score.
    """
    url = "https://www.nationsreportcard.gov/api/data"
    params = {
        "type": "data",
        "subject": subject,
        "grade": grade,
        "subscale": "MRPCM" if subject == "mathematics" else "RRPCM",
        "variable": "JURISDICTION",
        "jurisdiction": "NT",
        "stattype": "MN:MN",
        "Year": "2022",
    }
    abbr_to_name = {v: k for k, v in _state_name_to_abbr().items()}

    try:
        resp = requests.get(url, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("result", data.get("results", []))
        if isinstance(results, list) and len(results) >= 40:
            rows = []
            for r in results:
                name = r.get("jurisdiction", r.get("juris", ""))
                score = r.get("value", r.get("score", None))
                if score is not None:
                    try:
                        score = float(score)
                    except (ValueError, TypeError):
                        continue
                    abbr = _state_name_to_abbr().get(name)
                    if abbr:
                        rows.append({"state": abbr, "state_name": name, "score": score})
            if len(rows) >= 40:
                return pd.DataFrame(rows)
    except Exception:
        pass

    # Fallback to embedded data
    fallback = _NAEP_MATH_FALLBACK if subject == "mathematics" else _NAEP_READING_FALLBACK
    print(f"Using embedded NAEP {subject} data (fallback)")
    rows = []
    for abbr, score in fallback.items():
        rows.append({
            "state": abbr,
            "state_name": abbr_to_name.get(abbr, abbr),
            "score": float(score),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# FBI Crime Data
# ---------------------------------------------------------------------------

_FBI_CRIME_FALLBACK = {
    "AL": 453, "AK": 838, "AZ": 485, "AR": 580, "CA": 442,
    "CO": 424, "CT": 181, "DE": 431, "FL": 384, "GA": 374,
    "HI": 254, "ID": 227, "IL": 416, "IN": 382, "IA": 266,
    "KS": 404, "KY": 212, "LA": 564, "ME": 109, "MD": 448,
    "MA": 308, "MI": 461, "MN": 280, "MS": 291, "MO": 502,
    "MT": 404, "NE": 285, "NV": 460, "NH": 146, "NJ": 195,
    "NM": 832, "NY": 364, "NC": 407, "ND": 266, "OH": 309,
    "OK": 432, "OR": 292, "PA": 310, "RI": 220, "SC": 530,
    "SD": 399, "TN": 672, "TX": 446, "UT": 233, "VT": 173,
    "VA": 208, "WA": 367, "WV": 355, "WI": 296, "WY": 234,
    "DC": 812,
}


def fetch_fbi_crime_data(api_key: str, year: str = "2023") -> pd.DataFrame:
    """Fetch violent crime rates by state from the FBI Crime Data Explorer API.

    Returns a DataFrame with columns: state, state_name, violent_crime (per 100k).
    """
    abbr_to_name = {v: k for k, v in _state_name_to_abbr().items()}

    if api_key:
        try:
            # FBI Crime Data Explorer API v3
            url = f"https://api.usa.gov/crime/fbi/sapi/api/estimates/states"
            params = {"year": year, "API_KEY": api_key}
            resp = requests.get(url, params=params, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            results = data.get("results", data.get("data", []))
            if isinstance(results, list) and len(results) >= 40:
                rows = []
                for r in results:
                    abbr = r.get("state_abbr", r.get("state_abbrev", ""))
                    pop = r.get("population", 0)
                    violent = r.get("violent_crime", 0)
                    if abbr in abbr_to_name and pop and pop > 0:
                        rate = (violent / pop) * 100_000
                        rows.append({
                            "state": abbr,
                            "state_name": abbr_to_name.get(abbr, abbr),
                            "violent_crime": round(rate, 1),
                        })
                if len(rows) >= 40:
                    return pd.DataFrame(rows)
        except Exception:
            pass

    # Fallback to embedded data
    print("Using embedded FBI crime data (fallback)")
    rows = []
    for abbr, rate in _FBI_CRIME_FALLBACK.items():
        rows.append({
            "state": abbr,
            "state_name": abbr_to_name.get(abbr, abbr),
            "violent_crime": float(rate),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# CDC Infant Mortality
# ---------------------------------------------------------------------------

_CDC_INFANT_MORTALITY_FALLBACK = {
    "AL": 7.6, "AK": 5.8, "AZ": 5.5, "AR": 7.8, "CA": 4.2,
    "CO": 4.6, "CT": 4.4, "DE": 6.6, "FL": 6.1, "GA": 7.1,
    "HI": 5.4, "ID": 5.1, "IL": 6.1, "IN": 6.8, "IA": 4.9,
    "KS": 5.8, "KY": 6.5, "LA": 8.0, "ME": 5.6, "MD": 6.3,
    "MA": 3.7, "MI": 6.7, "MN": 4.8, "MS": 8.7, "MO": 6.4,
    "MT": 5.7, "NE": 5.3, "NV": 5.5, "NH": 4.2, "NJ": 4.1,
    "NM": 6.3, "NY": 4.3, "NC": 6.9, "ND": 6.0, "OH": 6.9,
    "OK": 7.2, "OR": 4.5, "PA": 5.9, "RI": 5.8, "SC": 6.8,
    "SD": 6.4, "TN": 7.1, "TX": 5.5, "UT": 4.7, "VT": 4.8,
    "VA": 5.6, "WA": 4.3, "WV": 7.0, "WI": 5.6, "WY": 6.1,
    "DC": 7.9,
}


def load_cdc_infant_mortality(path: Path = None) -> pd.DataFrame:
    """Load CDC infant mortality rates by state.

    If *path* is provided, reads from a downloaded CSV. Otherwise uses
    embedded fallback data.

    Returns a DataFrame with columns: state, state_name, infant_mort_rate.
    """
    abbr_to_name = {v: k for k, v in _state_name_to_abbr().items()}

    if path is not None and Path(path).exists():
        try:
            raw = pd.read_csv(path)
            raw.columns = [c.strip() for c in raw.columns]
            # Try to find state and rate columns
            state_col = [c for c in raw.columns if "state" in c.lower()]
            rate_col = [c for c in raw.columns if "rate" in c.lower() or "mort" in c.lower()]
            if state_col and rate_col:
                df = raw[[state_col[0], rate_col[0]]].copy()
                df.columns = ["state_name", "infant_mort_rate"]
                df["infant_mort_rate"] = pd.to_numeric(df["infant_mort_rate"], errors="coerce")
                df["state"] = df["state_name"].map(_state_name_to_abbr())
                df = df.dropna(subset=["state", "infant_mort_rate"]).reset_index(drop=True)
                if len(df) >= 40:
                    return df[["state", "state_name", "infant_mort_rate"]]
        except Exception:
            pass

    # Fallback to embedded data
    print("Using embedded CDC infant mortality data (fallback)")
    rows = []
    for abbr, rate in _CDC_INFANT_MORTALITY_FALLBACK.items():
        rows.append({
            "state": abbr,
            "state_name": abbr_to_name.get(abbr, abbr),
            "infant_mort_rate": rate,
        })
    return pd.DataFrame(rows)
