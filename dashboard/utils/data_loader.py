"""
Data loading utilities for the Stakeholder Ideology Dashboard.
"""

import pandas as pd
import json
from pathlib import Path
import streamlit as st

DATA_DIR = Path("/global/scratch/users/maxkagan/measuring_stakeholder_ideology/dashboard_data")


@st.cache_data(ttl=3600)
def load_poi_data(sampled=True):
    """Load POI data with coordinates and partisan lean.

    Args:
        sampled: If True, load pre-sampled 500k rows for faster performance.
                 If False, load full 9M row dataset.
    """
    if sampled:
        path = DATA_DIR / "poi_sampled.parquet"
        if path.exists():
            return pd.read_parquet(path)
    path = DATA_DIR / "poi_with_coords.parquet"
    if not path.exists():
        return None
    return pd.read_parquet(path)


@st.cache_data(ttl=3600)
def load_brand_summary():
    """Load brand-level summary statistics."""
    path = DATA_DIR / "brand_summary.parquet"
    if not path.exists():
        return None
    return pd.read_parquet(path)


@st.cache_data(ttl=3600)
def load_msa_summary():
    """Load MSA-level summary statistics."""
    path = DATA_DIR / "msa_summary.parquet"
    if not path.exists():
        return None
    return pd.read_parquet(path)


@st.cache_data(ttl=3600)
def load_filter_options():
    """Load available filter options (categories, NAICS codes)."""
    path = DATA_DIR / "filter_options.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def check_data_available():
    """Check if dashboard data is available."""
    required_files = [
        "poi_with_coords.parquet",
        "brand_summary.parquet",
        "msa_summary.parquet",
        "filter_options.json"
    ]
    missing = [f for f in required_files if not (DATA_DIR / f).exists()]
    return len(missing) == 0, missing


def filter_poi_by_viewport(df, lat_min, lat_max, lon_min, lon_max):
    """Filter POIs to a geographic viewport."""
    mask = (
        (df['latitude'] >= lat_min) &
        (df['latitude'] <= lat_max) &
        (df['longitude'] >= lon_min) &
        (df['longitude'] <= lon_max)
    )
    return df[mask]


def filter_poi_by_category(df, category):
    """Filter POIs by top_category."""
    if category and category != "All":
        return df[df['top_category'] == category]
    return df


def filter_poi_by_naics(df, naics_prefix, level=2):
    """Filter POIs by NAICS code prefix."""
    if naics_prefix and naics_prefix != "All":
        col = f'naics_{level}'
        if col in df.columns:
            return df[df[col] == naics_prefix]
    return df


def filter_poi_by_brand(df, brands):
    """Filter POIs by brand names."""
    if brands:
        return df[df['brand'].isin(brands)]
    return df
