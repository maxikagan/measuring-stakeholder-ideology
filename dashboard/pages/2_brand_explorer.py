"""
Brand Explorer - Search and compare brands by partisan lean.
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_brand_summary, load_poi_data
from utils.map_utils import create_scatter_layer, create_map_view, create_tooltip, create_deck

st.set_page_config(
    page_title="Brand Explorer",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Brand Explorer")
st.markdown("Search and compare brands by consumer partisan lean.")

brand_summary = load_brand_summary()

if brand_summary is None:
    st.error("Brand summary data not available.")
    st.stop()

with st.sidebar:
    st.header("Filters")

    min_locations = st.slider("Minimum locations", 1, 500, 50)

    sort_options = {
        "Number of locations": "n_locations",
        "Mean Rep Lean (2020)": "mean_rep_lean_2020",
        "Within-brand variation": "std_rep_lean_2020",
        "Number of MSAs": "n_msas",
    }
    sort_by = st.selectbox("Sort by", list(sort_options.keys()))
    sort_ascending = st.checkbox("Ascending order")

    st.header("Search")
    search_term = st.text_input("Search brand name")

filtered = brand_summary[brand_summary['n_locations'] >= min_locations].copy()

if search_term:
    filtered = filtered[filtered['brand'].str.contains(search_term, case=False, na=False)]

filtered = filtered.sort_values(sort_options[sort_by], ascending=sort_ascending)

st.subheader(f"Brands with {min_locations}+ Locations")
st.info(f"Found {len(filtered):,} brands matching criteria")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Brands", f"{len(filtered):,}")
with col2:
    mean_lean = filtered['mean_rep_lean_2020'].mean()
    st.metric("Avg Rep Lean", f"{mean_lean:.3f}")
with col3:
    mean_std = filtered['std_rep_lean_2020'].mean()
    st.metric("Avg Within-Brand Variation", f"{mean_std:.3f}" if pd.notna(mean_std) else "N/A")

display_cols = ['brand', 'n_locations', 'mean_rep_lean_2020', 'std_rep_lean_2020',
               'n_msas', 'n_states', 'top_category']

st.dataframe(
    filtered[display_cols].head(100).round(3),
    width="stretch",
    hide_index=True
)

st.markdown("---")

st.subheader("Brand Comparison")

available_brands = filtered['brand'].tolist()[:200]
selected_brands = st.multiselect(
    "Select brands to compare",
    options=available_brands,
    default=available_brands[:5] if len(available_brands) >= 5 else available_brands
)

if selected_brands:
    comparison = filtered[filtered['brand'].isin(selected_brands)].copy()
    comparison = comparison.sort_values('mean_rep_lean_2020')

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Mean Republican Lean (2020)**")
        chart_data = comparison.set_index('brand')['mean_rep_lean_2020']
        st.bar_chart(chart_data)

    with col2:
        st.markdown("**Within-Brand Variation (Std Dev)**")
        st.caption("Higher = more variation across locations")
        chart_data = comparison.set_index('brand')['std_rep_lean_2020']
        st.bar_chart(chart_data)

    st.markdown("---")

    st.subheader("Brand Location Map")

    poi_data = load_poi_data()
    if poi_data is not None:
        brand_pois = poi_data[poi_data['brand'].isin(selected_brands)]

        if len(brand_pois) > 10000:
            brand_pois = brand_pois.sample(n=10000, random_state=42)

        if len(brand_pois) > 0:
            view_state = create_map_view()
            layer = create_scatter_layer(brand_pois, scale=0.15, radius=200)
            tooltip = create_tooltip()
            deck = create_deck([layer], view_state, tooltip)
            st.pydeck_chart(deck)
        else:
            st.warning("No POI data available for selected brands.")
    else:
        st.warning("POI data not available for mapping.")

st.markdown("---")

st.subheader("Most/Least Republican Brands")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Most Republican Customers**")
    top_rep = filtered.nlargest(10, 'mean_rep_lean_2020')[['brand', 'mean_rep_lean_2020', 'n_locations']]
    st.dataframe(top_rep.round(3), width="stretch", hide_index=True)

with col2:
    st.markdown("**Most Democratic Customers**")
    top_dem = filtered.nsmallest(10, 'mean_rep_lean_2020')[['brand', 'mean_rep_lean_2020', 'n_locations']]
    st.dataframe(top_dem.round(3), width="stretch", hide_index=True)
