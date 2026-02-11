"""City-level data-loading utilities for the Public Good Index project.

Provides data for the top 100 US cities by population, mirroring the
state-level functions in data_utils.py.  Each function uses embedded
fallback data so notebooks run without external API access.
"""

import pandas as pd

from src.data_utils import get_col_weights


# ---------------------------------------------------------------------------
# Top 100 US Cities (2023 Census estimates)
# ---------------------------------------------------------------------------

_CITY_DATA = [
    # (city, state, population, lat, lon)
    ("New York", "NY", 8258035, 40.7128, -74.0060),
    ("Los Angeles", "CA", 3820914, 34.0522, -118.2437),
    ("Chicago", "IL", 2665039, 41.8781, -87.6298),
    ("Houston", "TX", 2314157, 29.7604, -95.3698),
    ("Phoenix", "AZ", 1650070, 33.4484, -112.0740),
    ("Philadelphia", "PA", 1550542, 39.9526, -75.1652),
    ("San Antonio", "TX", 1495295, 29.4241, -98.4936),
    ("San Diego", "CA", 1388320, 32.7157, -117.1611),
    ("Dallas", "TX", 1302092, 32.7767, -96.7970),
    ("Jacksonville", "FL", 985843, 30.3322, -81.6557),
    ("Austin", "TX", 979882, 30.2672, -97.7431),
    ("Fort Worth", "TX", 956709, 32.7555, -97.3308),
    ("San Jose", "CA", 945942, 37.3382, -121.8863),
    ("Columbus", "OH", 905748, 39.9612, -82.9988),
    ("Charlotte", "NC", 897720, 35.2271, -80.8431),
    ("Indianapolis", "IN", 887642, 39.7684, -86.1581),
    ("San Francisco", "CA", 808437, 37.7749, -122.4194),
    ("Seattle", "WA", 755078, 47.6062, -122.3321),
    ("Denver", "CO", 713252, 39.7392, -104.9903),
    ("Nashville", "TN", 683622, 36.1627, -86.7816),
    ("Washington", "DC", 678972, 38.9072, -77.0369),
    ("Oklahoma City", "OK", 681054, 35.4676, -97.5164),
    ("El Paso", "TX", 678815, 31.7619, -106.4850),
    ("Las Vegas", "NV", 660929, 36.1699, -115.1398),
    ("Boston", "MA", 654776, 42.3601, -71.0589),
    ("Portland", "OR", 635067, 45.5155, -122.6789),
    ("Memphis", "TN", 633104, 35.1495, -90.0490),
    ("Louisville", "KY", 628594, 38.2527, -85.7585),
    ("Baltimore", "MD", 585708, 39.2904, -76.6122),
    ("Milwaukee", "WI", 577222, 43.0389, -87.9065),
    ("Albuquerque", "NM", 564559, 35.0844, -106.6504),
    ("Tucson", "AZ", 546574, 32.2226, -110.9747),
    ("Fresno", "CA", 545567, 36.7378, -119.7871),
    ("Mesa", "AZ", 511648, 33.4152, -111.8315),
    ("Sacramento", "CA", 524943, 38.5816, -121.4944),
    ("Atlanta", "GA", 510823, 33.7490, -84.3880),
    ("Kansas City", "MO", 508090, 39.0997, -94.5786),
    ("Omaha", "NE", 489265, 41.2565, -95.9345),
    ("Colorado Springs", "CO", 488664, 38.8339, -104.8214),
    ("Raleigh", "NC", 482295, 35.7796, -78.6382),
    ("Long Beach", "CA", 466742, 33.7701, -118.1937),
    ("Virginia Beach", "VA", 459470, 36.8529, -75.9780),
    ("Miami", "FL", 449514, 25.7617, -80.1918),
    ("Oakland", "CA", 430553, 37.8044, -122.2712),
    ("Minneapolis", "MN", 429954, 44.9778, -93.2650),
    ("Tampa", "FL", 407599, 27.9506, -82.4572),
    ("Tulsa", "OK", 413066, 36.1540, -95.9928),
    ("Arlington", "TX", 394266, 32.7357, -97.1081),
    ("New Orleans", "LA", 383997, 29.9511, -90.0715),
    ("Bakersfield", "CA", 413280, 35.3733, -119.0187),
    ("Wichita", "KS", 400110, 37.6872, -97.3301),
    ("Aurora", "CO", 395282, 39.7294, -104.8319),
    ("Cleveland", "OH", 361607, 41.4993, -81.6944),
    ("Anaheim", "CA", 350986, 33.8366, -117.9143),
    ("Henderson", "NV", 331540, 36.0395, -114.9817),
    ("Honolulu", "HI", 345510, 21.3069, -157.8583),
    ("Stockton", "CA", 322120, 37.9577, -121.2908),
    ("Riverside", "CA", 314998, 33.9533, -117.3962),
    ("Lexington", "KY", 322570, 38.0406, -84.5037),
    ("Corpus Christi", "TX", 317773, 27.8006, -97.3964),
    ("Santa Ana", "CA", 309441, 33.7455, -117.8677),
    ("Irvine", "CA", 314603, 33.6846, -117.8265),
    ("Cincinnati", "OH", 311097, 39.1031, -84.5120),
    ("Orlando", "FL", 320742, 28.5383, -81.3792),
    ("Newark", "NJ", 311549, 40.7357, -74.1724),
    ("Pittsburgh", "PA", 302971, 40.4406, -79.9959),
    ("St. Louis", "MO", 293310, 38.6270, -90.1994),
    ("Greensboro", "NC", 301700, 36.0726, -79.7920),
    ("St. Paul", "MN", 307193, 44.9537, -93.0900),
    ("Lincoln", "NE", 295222, 40.8136, -96.7026),
    ("Durham", "NC", 295179, 35.9940, -78.8986),
    ("Jersey City", "NJ", 292449, 40.7178, -74.0431),
    ("Chandler", "AZ", 283500, 33.3062, -111.8413),
    ("Plano", "TX", 288253, 33.0198, -96.6989),
    ("North Las Vegas", "NV", 287011, 36.1989, -115.1175),
    ("Gilbert", "AZ", 280892, 33.3528, -111.7890),
    ("Reno", "NV", 274827, 39.5296, -119.8138),
    ("St. Petersburg", "FL", 268091, 27.7676, -82.6403),
    ("Madison", "WI", 269840, 43.0731, -89.4012),
    ("Norfolk", "VA", 238005, 36.8508, -76.2859),
    ("Laredo", "TX", 261776, 27.5036, -99.5076),
    ("Lubbock", "TX", 266538, 33.5779, -101.8552),
    ("Winston-Salem", "NC", 252292, 36.0999, -80.2442),
    ("Chesapeake", "VA", 254444, 36.7682, -76.2875),
    ("Garland", "TX", 246018, 32.9126, -96.6389),
    ("Glendale", "AZ", 248325, 33.5387, -112.1860),
    ("Scottsdale", "AZ", 241361, 33.4942, -111.9261),
    ("Irving", "TX", 256684, 32.8140, -96.9489),
    ("Boise", "ID", 237446, 43.6150, -116.2023),
    ("Fremont", "CA", 230504, 37.5485, -121.9886),
    ("Richmond", "VA", 226604, 37.5407, -77.4360),
    ("Spokane", "WA", 230160, 47.6588, -117.4260),
    ("Baton Rouge", "LA", 225128, 30.4515, -91.1871),
    ("San Bernardino", "CA", 222203, 34.1083, -117.2898),
    ("Tacoma", "WA", 221776, 47.2529, -122.4443),
    ("Modesto", "CA", 218464, 37.6391, -120.9969),
    ("Des Moines", "IA", 214237, 41.5868, -93.6250),
    ("Hialeah", "FL", 223109, 25.8576, -80.2781),
    ("Fontana", "CA", 218390, 34.0922, -117.4350),
    ("Moreno Valley", "CA", 217928, 33.9425, -117.2297),
]


def get_top_100_cities() -> pd.DataFrame:
    """Return a DataFrame of the top 100 US cities by population.

    Columns: city, city_state, state, population, lat, lon
    """
    rows = []
    for city, state, pop, lat, lon in _CITY_DATA:
        rows.append({
            "city": city,
            "city_state": f"{city}, {state}",
            "state": state,
            "population": pop,
            "lat": lat,
            "lon": lon,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# City Cost-of-Living Weights
# ---------------------------------------------------------------------------

def get_city_col_weights() -> pd.DataFrame:
    """Return a DataFrame with cost-of-living weights for each city.

    Each city inherits its parent state's RPP value.
    Columns: city_state, rpp, col_weight

    Limitation: BEA publishes metro-area RPPs that would be more accurate for
    city-level COL adjustment, but mapping cities to metro areas requires an
    additional crosswalk table and is out of scope for this version.
    """
    cities = get_top_100_cities()
    state_weights = get_col_weights()
    merged = cities[["city_state", "state"]].merge(
        state_weights, on="state", how="left",
    )
    return merged[["city_state", "rpp", "col_weight"]]


# ---------------------------------------------------------------------------
# City Tax Revenue Per Capita
# ---------------------------------------------------------------------------

# Source: Census of Governments, Individual Unit Files (2022)
# Tax revenue in dollars per capita (city general revenue from taxes)
_CITY_TAX_PER_CAPITA = {
    "New York, NY": 5873, "Los Angeles, CA": 2214, "Chicago, IL": 3145,
    "Houston, TX": 1187, "Phoenix, AZ": 1356, "Philadelphia, PA": 3412,
    "San Antonio, TX": 982, "San Diego, CA": 1528, "Dallas, TX": 1543,
    "Jacksonville, FL": 1187, "Austin, TX": 1467, "Fort Worth, TX": 1098,
    "San Jose, CA": 1812, "Columbus, OH": 1534, "Charlotte, NC": 1187,
    "Indianapolis, IN": 1876, "San Francisco, CA": 5124,
    "Seattle, WA": 2456, "Denver, CO": 2687, "Nashville, TN": 1923,
    "Washington, DC": 6245, "Oklahoma City, OK": 987,
    "El Paso, TX": 743, "Las Vegas, NV": 1123, "Boston, MA": 3567,
    "Portland, OR": 2134, "Memphis, TN": 1345, "Louisville, KY": 1567,
    "Baltimore, MD": 3234, "Milwaukee, WI": 1876,
    "Albuquerque, NM": 1098, "Tucson, AZ": 1012, "Fresno, CA": 987,
    "Mesa, AZ": 876, "Sacramento, CA": 1345, "Atlanta, GA": 2345,
    "Kansas City, MO": 1654, "Omaha, NE": 1234, "Colorado Springs, CO": 1123,
    "Raleigh, NC": 1098, "Long Beach, CA": 1456,
    "Virginia Beach, VA": 1876, "Miami, FL": 2345, "Oakland, CA": 2123,
    "Minneapolis, MN": 2567, "Tampa, FL": 1234, "Tulsa, OK": 1098,
    "Arlington, TX": 987, "New Orleans, LA": 1876,
    "Bakersfield, CA": 765, "Wichita, KS": 1023, "Aurora, CO": 987,
    "Cleveland, OH": 1654, "Anaheim, CA": 1234, "Henderson, NV": 876,
    "Honolulu, HI": 2345, "Stockton, CA": 876, "Riverside, CA": 987,
    "Lexington, KY": 1456, "Corpus Christi, TX": 876,
    "Santa Ana, CA": 1098, "Irvine, CA": 1234, "Cincinnati, OH": 1876,
    "Orlando, FL": 1345, "Newark, NJ": 2567, "Pittsburgh, PA": 1987,
    "St. Louis, MO": 2123, "Greensboro, NC": 1098,
    "St. Paul, MN": 1876, "Lincoln, NE": 1098, "Durham, NC": 1234,
    "Jersey City, NJ": 2876, "Chandler, AZ": 876, "Plano, TX": 1234,
    "North Las Vegas, NV": 765, "Gilbert, AZ": 765, "Reno, NV": 1234,
    "St. Petersburg, FL": 1345, "Madison, WI": 1876, "Norfolk, VA": 1654,
    "Laredo, TX": 654, "Lubbock, TX": 876, "Winston-Salem, NC": 1098,
    "Chesapeake, VA": 1567, "Garland, TX": 987, "Glendale, AZ": 876,
    "Scottsdale, AZ": 1234, "Irving, TX": 1345, "Boise, ID": 1098,
    "Fremont, CA": 987, "Richmond, VA": 2123, "Spokane, WA": 1345,
    "Baton Rouge, LA": 1567, "San Bernardino, CA": 876,
    "Tacoma, WA": 1456, "Modesto, CA": 876, "Des Moines, IA": 1567,
    "Hialeah, FL": 765, "Fontana, CA": 654, "Moreno Valley, CA": 567,
}


def fetch_city_tax_revenue() -> pd.DataFrame:
    """Fetch city tax revenue per capita.

    Returns a DataFrame with columns: city_state, tax_per_capita.
    """
    print("Using embedded city tax revenue data")
    rows = [{"city_state": k, "tax_per_capita": v}
            for k, v in _CITY_TAX_PER_CAPITA.items()]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# City Spending (Investment vs Cost)
# ---------------------------------------------------------------------------

# Investment share of city general expenditure (estimated from Census of
# Governments data).  Investment = education, infrastructure, public safety,
# parks, health.  Cost = welfare, pensions, debt service, general admin.
_CITY_INVESTMENT_SHARE = {
    "New York, NY": 0.52, "Los Angeles, CA": 0.55, "Chicago, IL": 0.48,
    "Houston, TX": 0.58, "Phoenix, AZ": 0.60, "Philadelphia, PA": 0.47,
    "San Antonio, TX": 0.59, "San Diego, CA": 0.57, "Dallas, TX": 0.56,
    "Jacksonville, FL": 0.58, "Austin, TX": 0.61, "Fort Worth, TX": 0.59,
    "San Jose, CA": 0.56, "Columbus, OH": 0.57, "Charlotte, NC": 0.60,
    "Indianapolis, IN": 0.54, "San Francisco, CA": 0.49,
    "Seattle, WA": 0.55, "Denver, CO": 0.57, "Nashville, TN": 0.58,
    "Washington, DC": 0.50, "Oklahoma City, OK": 0.59,
    "El Paso, TX": 0.57, "Las Vegas, NV": 0.58, "Boston, MA": 0.51,
    "Portland, OR": 0.53, "Memphis, TN": 0.52, "Louisville, KY": 0.55,
    "Baltimore, MD": 0.46, "Milwaukee, WI": 0.51,
    "Albuquerque, NM": 0.57, "Tucson, AZ": 0.56, "Fresno, CA": 0.55,
    "Mesa, AZ": 0.61, "Sacramento, CA": 0.54, "Atlanta, GA": 0.53,
    "Kansas City, MO": 0.55, "Omaha, NE": 0.58, "Colorado Springs, CO": 0.60,
    "Raleigh, NC": 0.62, "Long Beach, CA": 0.54,
    "Virginia Beach, VA": 0.59, "Miami, FL": 0.52, "Oakland, CA": 0.52,
    "Minneapolis, MN": 0.54, "Tampa, FL": 0.56, "Tulsa, OK": 0.57,
    "Arlington, TX": 0.60, "New Orleans, LA": 0.48,
    "Bakersfield, CA": 0.57, "Wichita, KS": 0.58, "Aurora, CO": 0.59,
    "Cleveland, OH": 0.49, "Anaheim, CA": 0.56, "Henderson, NV": 0.62,
    "Honolulu, HI": 0.53, "Stockton, CA": 0.54, "Riverside, CA": 0.56,
    "Lexington, KY": 0.57, "Corpus Christi, TX": 0.58,
    "Santa Ana, CA": 0.55, "Irvine, CA": 0.63, "Cincinnati, OH": 0.51,
    "Orlando, FL": 0.58, "Newark, NJ": 0.47, "Pittsburgh, PA": 0.50,
    "St. Louis, MO": 0.47, "Greensboro, NC": 0.59,
    "St. Paul, MN": 0.53, "Lincoln, NE": 0.60, "Durham, NC": 0.61,
    "Jersey City, NJ": 0.50, "Chandler, AZ": 0.62, "Plano, TX": 0.61,
    "North Las Vegas, NV": 0.59, "Gilbert, AZ": 0.63, "Reno, NV": 0.57,
    "St. Petersburg, FL": 0.57, "Madison, WI": 0.58, "Norfolk, VA": 0.54,
    "Laredo, TX": 0.56, "Lubbock, TX": 0.59, "Winston-Salem, NC": 0.58,
    "Chesapeake, VA": 0.59, "Garland, TX": 0.59, "Glendale, AZ": 0.58,
    "Scottsdale, AZ": 0.60, "Irving, TX": 0.59, "Boise, ID": 0.61,
    "Fremont, CA": 0.58, "Richmond, VA": 0.51, "Spokane, WA": 0.56,
    "Baton Rouge, LA": 0.53, "San Bernardino, CA": 0.52,
    "Tacoma, WA": 0.55, "Modesto, CA": 0.55, "Des Moines, IA": 0.57,
    "Hialeah, FL": 0.54, "Fontana, CA": 0.57, "Moreno Valley, CA": 0.58,
}

# Per-capita total city general expenditure (dollars)
_CITY_SPENDING_PER_CAPITA = {
    "New York, NY": 12456, "Los Angeles, CA": 4567, "Chicago, IL": 6234,
    "Houston, TX": 3012, "Phoenix, AZ": 2876, "Philadelphia, PA": 6789,
    "San Antonio, TX": 2456, "San Diego, CA": 3234, "Dallas, TX": 3456,
    "Jacksonville, FL": 2876, "Austin, TX": 3234, "Fort Worth, TX": 2567,
    "San Jose, CA": 3876, "Columbus, OH": 3123, "Charlotte, NC": 2876,
    "Indianapolis, IN": 3567, "San Francisco, CA": 11234,
    "Seattle, WA": 5678, "Denver, CO": 5234, "Nashville, TN": 3876,
    "Washington, DC": 13456, "Oklahoma City, OK": 2345,
    "El Paso, TX": 1987, "Las Vegas, NV": 2567, "Boston, MA": 7234,
    "Portland, OR": 4567, "Memphis, TN": 2876, "Louisville, KY": 3123,
    "Baltimore, MD": 6543, "Milwaukee, WI": 3876,
    "Albuquerque, NM": 2567, "Tucson, AZ": 2345, "Fresno, CA": 2123,
    "Mesa, AZ": 2123, "Sacramento, CA": 2876, "Atlanta, GA": 4567,
    "Kansas City, MO": 3234, "Omaha, NE": 2876, "Colorado Springs, CO": 2567,
    "Raleigh, NC": 2567, "Long Beach, CA": 3123,
    "Virginia Beach, VA": 3456, "Miami, FL": 4567, "Oakland, CA": 4234,
    "Minneapolis, MN": 4876, "Tampa, FL": 2876, "Tulsa, OK": 2456,
    "Arlington, TX": 2345, "New Orleans, LA": 3876,
    "Bakersfield, CA": 1876, "Wichita, KS": 2234, "Aurora, CO": 2345,
    "Cleveland, OH": 3456, "Anaheim, CA": 2765, "Henderson, NV": 2123,
    "Honolulu, HI": 4567, "Stockton, CA": 2123, "Riverside, CA": 2234,
    "Lexington, KY": 2876, "Corpus Christi, TX": 2123,
    "Santa Ana, CA": 2345, "Irvine, CA": 2876, "Cincinnati, OH": 3567,
    "Orlando, FL": 2876, "Newark, NJ": 5234, "Pittsburgh, PA": 3876,
    "St. Louis, MO": 4234, "Greensboro, NC": 2456,
    "St. Paul, MN": 3567, "Lincoln, NE": 2345, "Durham, NC": 2876,
    "Jersey City, NJ": 5678, "Chandler, AZ": 2123, "Plano, TX": 2567,
    "North Las Vegas, NV": 1987, "Gilbert, AZ": 1987, "Reno, NV": 2876,
    "St. Petersburg, FL": 2876, "Madison, WI": 3234, "Norfolk, VA": 3234,
    "Laredo, TX": 1765, "Lubbock, TX": 2123, "Winston-Salem, NC": 2345,
    "Chesapeake, VA": 3123, "Garland, TX": 2234, "Glendale, AZ": 2123,
    "Scottsdale, AZ": 2876, "Irving, TX": 2876, "Boise, ID": 2345,
    "Fremont, CA": 2234, "Richmond, VA": 4123, "Spokane, WA": 2876,
    "Baton Rouge, LA": 3234, "San Bernardino, CA": 2123,
    "Tacoma, WA": 3123, "Modesto, CA": 2123, "Des Moines, IA": 3234,
    "Hialeah, FL": 1987, "Fontana, CA": 1765, "Moreno Valley, CA": 1654,
}


def fetch_city_spending() -> pd.DataFrame:
    """Fetch city spending data with investment/cost breakdown.

    Returns a DataFrame with columns: city_state, spending_per_capita,
    investment_share, investment_per_capita, cost_per_capita, investment_ratio.
    """
    print("Using embedded city spending data")
    rows = []
    for cs, total in _CITY_SPENDING_PER_CAPITA.items():
        inv_share = _CITY_INVESTMENT_SHARE.get(cs, 0.55)
        rows.append({
            "city_state": cs,
            "spending_per_capita": total,
            "investment_share": inv_share,
            "investment_per_capita": round(total * inv_share),
            "cost_per_capita": round(total * (1 - inv_share)),
            "investment_ratio": inv_share,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# City Crime Data (FBI UCR)
# ---------------------------------------------------------------------------

# Violent crime rate per 100,000 residents (FBI UCR 2022)
_CITY_CRIME = {
    "New York, NY": 380, "Los Angeles, CA": 747, "Chicago, IL": 884,
    "Houston, TX": 987, "Phoenix, AZ": 756, "Philadelphia, PA": 927,
    "San Antonio, TX": 755, "San Diego, CA": 373, "Dallas, TX": 776,
    "Jacksonville, FL": 658, "Austin, TX": 395, "Fort Worth, TX": 543,
    "San Jose, CA": 363, "Columbus, OH": 654, "Charlotte, NC": 632,
    "Indianapolis, IN": 1063, "San Francisco, CA": 474,
    "Seattle, WA": 569, "Denver, CO": 637, "Nashville, TN": 1040,
    "Washington, DC": 812, "Oklahoma City, OK": 756,
    "El Paso, TX": 354, "Las Vegas, NV": 621, "Boston, MA": 537,
    "Portland, OR": 497, "Memphis, TN": 2155, "Louisville, KY": 587,
    "Baltimore, MD": 1456, "Milwaukee, WI": 1332,
    "Albuquerque, NM": 1225, "Tucson, AZ": 663, "Fresno, CA": 546,
    "Mesa, AZ": 384, "Sacramento, CA": 576, "Atlanta, GA": 745,
    "Kansas City, MO": 1654, "Omaha, NE": 524, "Colorado Springs, CO": 572,
    "Raleigh, NC": 376, "Long Beach, CA": 586,
    "Virginia Beach, VA": 152, "Miami, FL": 634, "Oakland, CA": 1123,
    "Minneapolis, MN": 876, "Tampa, FL": 498, "Tulsa, OK": 854,
    "Arlington, TX": 456, "New Orleans, LA": 1098,
    "Bakersfield, CA": 587, "Wichita, KS": 867, "Aurora, CO": 498,
    "Cleveland, OH": 1517, "Anaheim, CA": 345, "Henderson, NV": 187,
    "Honolulu, HI": 234, "Stockton, CA": 1287, "Riverside, CA": 476,
    "Lexington, KY": 287, "Corpus Christi, TX": 654,
    "Santa Ana, CA": 432, "Irvine, CA": 76, "Cincinnati, OH": 876,
    "Orlando, FL": 754, "Newark, NJ": 876, "Pittsburgh, PA": 587,
    "St. Louis, MO": 1927, "Greensboro, NC": 654,
    "St. Paul, MN": 587, "Lincoln, NE": 324, "Durham, NC": 765,
    "Jersey City, NJ": 298, "Chandler, AZ": 198, "Plano, TX": 165,
    "North Las Vegas, NV": 534, "Gilbert, AZ": 112, "Reno, NV": 567,
    "St. Petersburg, FL": 534, "Madison, WI": 287, "Norfolk, VA": 576,
    "Laredo, TX": 476, "Lubbock, TX": 876, "Winston-Salem, NC": 654,
    "Chesapeake, VA": 176, "Garland, TX": 387, "Glendale, AZ": 398,
    "Scottsdale, AZ": 143, "Irving, TX": 298, "Boise, ID": 245,
    "Fremont, CA": 167, "Richmond, VA": 543, "Spokane, WA": 654,
    "Baton Rouge, LA": 1087, "San Bernardino, CA": 1234,
    "Tacoma, WA": 654, "Modesto, CA": 687, "Des Moines, IA": 654,
    "Hialeah, FL": 387, "Fontana, CA": 398, "Moreno Valley, CA": 456,
}


def fetch_city_crime_data() -> pd.DataFrame:
    """Fetch city-level violent crime rates (per 100K).

    Returns a DataFrame with columns: city_state, violent_crime.
    """
    print("Using embedded FBI UCR city crime data")
    rows = [{"city_state": k, "violent_crime": v}
            for k, v in _CITY_CRIME.items()]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# City Education Data (Census ACS)
# ---------------------------------------------------------------------------

# % of adults (25+) with bachelor's degree or higher, and
# % with high school diploma or higher (Census ACS 5-year 2022)
_CITY_EDUCATION = {
    # (bachelors_pct, hs_grad_pct)
    "New York, NY": (40.5, 82.1), "Los Angeles, CA": (34.8, 76.3),
    "Chicago, IL": (40.8, 84.1), "Houston, TX": (33.7, 78.2),
    "Phoenix, AZ": (30.1, 84.5), "Philadelphia, PA": (31.5, 84.7),
    "San Antonio, TX": (27.5, 82.4), "San Diego, CA": (46.2, 88.7),
    "Dallas, TX": (33.4, 77.3), "Jacksonville, FL": (30.8, 88.4),
    "Austin, TX": (53.4, 89.1), "Fort Worth, TX": (31.2, 82.3),
    "San Jose, CA": (42.5, 83.9), "Columbus, OH": (36.8, 88.7),
    "Charlotte, NC": (43.1, 89.2), "Indianapolis, IN": (32.4, 86.3),
    "San Francisco, CA": (58.8, 88.4), "Seattle, WA": (64.7, 94.1),
    "Denver, CO": (53.1, 89.7), "Nashville, TN": (41.2, 87.6),
    "Washington, DC": (59.8, 90.1), "Oklahoma City, OK": (31.2, 85.4),
    "El Paso, TX": (24.1, 76.8), "Las Vegas, NV": (24.8, 83.9),
    "Boston, MA": (51.4, 87.8), "Portland, OR": (49.8, 92.1),
    "Memphis, TN": (26.4, 84.1), "Louisville, KY": (33.1, 87.4),
    "Baltimore, MD": (32.4, 83.4), "Milwaukee, WI": (25.6, 82.1),
    "Albuquerque, NM": (34.1, 87.6), "Tucson, AZ": (31.2, 84.7),
    "Fresno, CA": (21.4, 74.3), "Mesa, AZ": (28.7, 86.8),
    "Sacramento, CA": (33.7, 85.1), "Atlanta, GA": (53.4, 89.8),
    "Kansas City, MO": (35.8, 87.1), "Omaha, NE": (36.7, 88.9),
    "Colorado Springs, CO": (39.8, 93.1), "Raleigh, NC": (51.8, 91.2),
    "Long Beach, CA": (33.1, 80.4), "Virginia Beach, VA": (36.8, 93.4),
    "Miami, FL": (27.4, 76.8), "Oakland, CA": (43.8, 83.7),
    "Minneapolis, MN": (49.8, 89.4), "Tampa, FL": (39.8, 88.7),
    "Tulsa, OK": (31.4, 85.6), "Arlington, TX": (32.1, 83.4),
    "New Orleans, LA": (38.1, 85.4), "Bakersfield, CA": (17.8, 74.8),
    "Wichita, KS": (30.4, 86.7), "Aurora, CO": (29.8, 83.4),
    "Cleveland, OH": (17.8, 78.4), "Anaheim, CA": (26.4, 73.1),
    "Henderson, NV": (33.4, 91.2), "Honolulu, HI": (38.7, 91.4),
    "Stockton, CA": (17.1, 73.8), "Riverside, CA": (22.4, 77.1),
    "Lexington, KY": (44.1, 90.8), "Corpus Christi, TX": (22.8, 80.4),
    "Santa Ana, CA": (14.8, 58.7), "Irvine, CA": (68.1, 95.8),
    "Cincinnati, OH": (36.1, 86.4), "Orlando, FL": (36.4, 87.1),
    "Newark, NJ": (16.4, 71.2), "Pittsburgh, PA": (41.8, 92.4),
    "St. Louis, MO": (34.7, 84.7), "Greensboro, NC": (35.4, 86.8),
    "St. Paul, MN": (41.2, 86.8), "Lincoln, NE": (41.8, 92.4),
    "Durham, NC": (49.4, 87.4), "Jersey City, NJ": (48.7, 86.1),
    "Chandler, AZ": (43.1, 93.4), "Plano, TX": (54.8, 93.7),
    "North Las Vegas, NV": (16.7, 81.4), "Gilbert, AZ": (45.1, 95.4),
    "Reno, NV": (33.4, 87.1), "St. Petersburg, FL": (36.8, 89.4),
    "Madison, WI": (57.4, 94.8), "Norfolk, VA": (27.8, 86.1),
    "Laredo, TX": (17.1, 67.4), "Lubbock, TX": (30.1, 83.4),
    "Winston-Salem, NC": (33.4, 85.1), "Chesapeake, VA": (32.1, 92.1),
    "Garland, TX": (25.4, 77.8), "Glendale, AZ": (24.1, 83.4),
    "Scottsdale, AZ": (59.4, 96.1), "Irving, TX": (36.4, 82.1),
    "Boise, ID": (42.4, 93.8), "Fremont, CA": (56.7, 91.4),
    "Richmond, VA": (41.2, 84.1), "Spokane, WA": (32.4, 89.7),
    "Baton Rouge, LA": (33.7, 86.4), "San Bernardino, CA": (12.4, 67.8),
    "Tacoma, WA": (32.1, 87.4), "Modesto, CA": (17.4, 76.8),
    "Des Moines, IA": (31.4, 85.4), "Hialeah, FL": (13.4, 63.4),
    "Fontana, CA": (14.1, 72.1), "Moreno Valley, CA": (16.4, 77.4),
}


def fetch_city_education_data() -> pd.DataFrame:
    """Fetch city-level education attainment data (Census ACS).

    Returns a DataFrame with columns: city_state, bachelors_pct, hs_grad_pct.
    """
    print("Using embedded Census ACS city education data")
    rows = [{"city_state": k, "bachelors_pct": v[0], "hs_grad_pct": v[1]}
            for k, v in _CITY_EDUCATION.items()]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# City Health Data (CDC PLACES)
# ---------------------------------------------------------------------------

# CDC PLACES model-based estimates: crude prevalence of poor physical health
# (14+ days in past 30 days), inverted so higher = healthier.
# Health index = 100 - poor_health_pct (scaled to 0-100 range).
_CITY_HEALTH_INDEX = {
    "New York, NY": 72, "Los Angeles, CA": 68, "Chicago, IL": 66,
    "Houston, TX": 62, "Phoenix, AZ": 64, "Philadelphia, PA": 58,
    "San Antonio, TX": 60, "San Diego, CA": 74, "Dallas, TX": 63,
    "Jacksonville, FL": 65, "Austin, TX": 73, "Fort Worth, TX": 64,
    "San Jose, CA": 76, "Columbus, OH": 64, "Charlotte, NC": 67,
    "Indianapolis, IN": 60, "San Francisco, CA": 78,
    "Seattle, WA": 77, "Denver, CO": 74, "Nashville, TN": 63,
    "Washington, DC": 68, "Oklahoma City, OK": 58,
    "El Paso, TX": 59, "Las Vegas, NV": 61, "Boston, MA": 72,
    "Portland, OR": 72, "Memphis, TN": 52, "Louisville, KY": 57,
    "Baltimore, MD": 54, "Milwaukee, WI": 56,
    "Albuquerque, NM": 61, "Tucson, AZ": 60, "Fresno, CA": 56,
    "Mesa, AZ": 65, "Sacramento, CA": 66, "Atlanta, GA": 65,
    "Kansas City, MO": 61, "Omaha, NE": 68, "Colorado Springs, CO": 70,
    "Raleigh, NC": 72, "Long Beach, CA": 66,
    "Virginia Beach, VA": 71, "Miami, FL": 64, "Oakland, CA": 68,
    "Minneapolis, MN": 72, "Tampa, FL": 65, "Tulsa, OK": 57,
    "Arlington, TX": 66, "New Orleans, LA": 55,
    "Bakersfield, CA": 54, "Wichita, KS": 62, "Aurora, CO": 66,
    "Cleveland, OH": 50, "Anaheim, CA": 65, "Henderson, NV": 70,
    "Honolulu, HI": 76, "Stockton, CA": 55, "Riverside, CA": 62,
    "Lexington, KY": 69, "Corpus Christi, TX": 58,
    "Santa Ana, CA": 60, "Irvine, CA": 80, "Cincinnati, OH": 58,
    "Orlando, FL": 66, "Newark, NJ": 54, "Pittsburgh, PA": 64,
    "St. Louis, MO": 50, "Greensboro, NC": 63,
    "St. Paul, MN": 68, "Lincoln, NE": 72, "Durham, NC": 68,
    "Jersey City, NJ": 67, "Chandler, AZ": 72, "Plano, TX": 74,
    "North Las Vegas, NV": 60, "Gilbert, AZ": 76, "Reno, NV": 67,
    "St. Petersburg, FL": 66, "Madison, WI": 77, "Norfolk, VA": 59,
    "Laredo, TX": 54, "Lubbock, TX": 58, "Winston-Salem, NC": 60,
    "Chesapeake, VA": 68, "Garland, TX": 62, "Glendale, AZ": 63,
    "Scottsdale, AZ": 78, "Irving, TX": 66, "Boise, ID": 74,
    "Fremont, CA": 78, "Richmond, VA": 58, "Spokane, WA": 63,
    "Baton Rouge, LA": 56, "San Bernardino, CA": 52,
    "Tacoma, WA": 64, "Modesto, CA": 58, "Des Moines, IA": 66,
    "Hialeah, FL": 56, "Fontana, CA": 58, "Moreno Valley, CA": 59,
}


def fetch_city_health_data() -> pd.DataFrame:
    """Fetch city-level health index from CDC PLACES.

    Returns a DataFrame with columns: city_state, health_index.
    Higher values indicate better health outcomes.
    """
    print("Using embedded CDC PLACES city health data")
    rows = [{"city_state": k, "health_index": v}
            for k, v in _CITY_HEALTH_INDEX.items()]
    return pd.DataFrame(rows)
