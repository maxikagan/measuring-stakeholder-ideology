"""
MSA Analysis - Explore partisan lean by metropolitan area.
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_msa_summary, load_poi_data, load_brand_summary
from utils.map_utils import create_scatter_layer, create_map_view, create_tooltip, create_deck

st.set_page_config(
    page_title="MSA Analysis",
    page_icon="🌆",
    layout="wide"
)

st.title("🌆 MSA Analysis")
st.markdown("Explore partisan lean by metropolitan statistical area.")

msa_summary = load_msa_summary()

if msa_summary is None:
    st.error("MSA summary data not available.")
    st.stop()

with st.sidebar:
    st.header("Filters")

    min_pois = st.slider("Minimum POIs", 100, 10000, 1000)

    sort_options = {
        "Number of POIs": "n_pois",
        "Mean Rep Lean (2020)": "mean_rep_lean_2020",
        "Within-MSA Variation": "std_rep_lean_2020",
        "Total Visitors": "total_visitors",
    }
    sort_by = st.selectbox("Sort by", list(sort_options.keys()))
    sort_ascending = st.checkbox("Ascending order")

    st.header("Search")
    search_term = st.text_input("Search MSA name")

filtered = msa_summary[msa_summary['n_pois'] >= min_pois].copy()

if search_term:
    filtered = filtered[filtered['cbsa_title'].str.contains(search_term, case=False, na=False)]

filtered = filtered.sort_values(sort_options[sort_by], ascending=sort_ascending)

st.subheader(f"MSAs with {min_pois}+ POIs")
st.info(f"Found {len(filtered):,} MSAs matching criteria")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total MSAs", f"{len(filtered):,}")
with col2:
    mean_lean = filtered['mean_rep_lean_2020'].mean()
    st.metric("Avg Rep Lean", f"{mean_lean:.3f}")
with col3:
    mean_std = filtered['std_rep_lean_2020'].mean()
    st.metric("Avg Within-MSA Variation", f"{mean_std:.3f}")

display_cols = ['cbsa_title', 'n_pois', 'mean_rep_lean_2020', 'std_rep_lean_2020',
               'n_branded_pois', 'region']

st.dataframe(
    filtered[display_cols].head(50).round(3),
    width="stretch",
    hide_index=True
)

st.markdown("---")

st.subheader("Within-MSA Brand Analysis")

selected_msa = st.selectbox(
    "Select an MSA to explore",
    options=filtered['cbsa_title'].tolist(),
    index=0 if len(filtered) > 0 else None
)

if selected_msa:
    poi_data = load_poi_data()
    brand_summary = load_brand_summary()

    if poi_data is not None:
        msa_pois = poi_data[poi_data['cbsa_title'] == selected_msa]

        st.markdown(f"**{selected_msa}**: {len(msa_pois):,} POIs")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("POIs", f"{len(msa_pois):,}")
        with col2:
            st.metric("Unique Brands", f"{msa_pois['brand'].nunique():,}")
        with col3:
            mean_lean = msa_pois['mean_rep_lean_2020'].mean()
            st.metric("Mean Rep Lean", f"{mean_lean:.3f}")

        msa_brands = msa_pois[msa_pois['brand'].notna()].groupby('brand').agg({
            'placekey': 'count',
            'mean_rep_lean_2020': ['mean', 'std'],
            'total_visitors': 'sum',
        }).reset_index()
        msa_brands.columns = ['brand', 'locations', 'mean_rep_lean', 'std_rep_lean', 'total_visitors']
        msa_brands = msa_brands[msa_brands['locations'] >= 3]
        msa_brands = msa_brands.sort_values('mean_rep_lean', ascending=False)

        st.markdown("**Brands in this MSA (3+ locations)**")
        st.dataframe(msa_brands.head(30).round(3), width="stretch", hide_index=True)

        st.markdown("---")

        st.subheader("Map of Selected MSA")

        if len(msa_pois) > 5000:
            map_pois = msa_pois.sample(n=5000, random_state=42)
        else:
            map_pois = msa_pois

        center_lat = map_pois['latitude'].mean()
        center_lon = map_pois['longitude'].mean()

        view_state = create_map_view(center_lat, center_lon, zoom=10)
        layer = create_scatter_layer(map_pois, scale=0.15, radius=100)
        tooltip = create_tooltip()
        deck = create_deck([layer], view_state, tooltip)
        st.pydeck_chart(deck)

    else:
        st.warning("POI data not available for detailed analysis.")

st.markdown("---")

st.subheader("Most/Least Republican MSAs")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Most Republican MSAs**")
    top_rep = filtered.nlargest(10, 'mean_rep_lean_2020')[['cbsa_title', 'mean_rep_lean_2020', 'n_pois']]
    st.dataframe(top_rep.round(3), width="stretch", hide_index=True)

with col2:
    st.markdown("**Most Democratic MSAs**")
    top_dem = filtered.nsmallest(10, 'mean_rep_lean_2020')[['cbsa_title', 'mean_rep_lean_2020', 'n_pois']]
    st.dataframe(top_dem.round(3), width="stretch", hide_index=True)
