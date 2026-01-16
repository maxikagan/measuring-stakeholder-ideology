"""
Neighbor Comparison Map - Interactive POI visualization.

Shows POIs colored by excess partisan lean (deviation from local neighbors).
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import (
    load_poi_data,
    load_filter_options,
    filter_poi_by_category,
    filter_poi_by_naics,
)
from utils.map_utils import (
    create_scatter_layer,
    create_map_view,
    create_tooltip,
    create_deck,
)

st.set_page_config(
    page_title="Neighbor Map",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Partisan Lean Map")
st.markdown("""
POIs colored by **consumer partisan lean** - red indicates more Republican customers,
blue indicates more Democratic customers. Filter by category or NAICS to compare similar businesses.
""")


@st.cache_data(ttl=3600)
def get_sampled_data(category, naics_2, sample_size=50000):
    """Load and sample POI data for performance."""
    df = load_poi_data()
    if df is None:
        return None

    df = filter_poi_by_category(df, category)
    df = filter_poi_by_naics(df, naics_2, level=2)

    if len(df) > sample_size:
        df = df.sample(n=sample_size, random_state=42)

    return df


with st.sidebar:
    st.header("Filters")

    filter_opts = load_filter_options()

    if filter_opts:
        categories = ["All"] + [c['category'] for c in filter_opts.get('categories', [])]
        selected_category = st.selectbox("Category", categories, index=0)

        naics_codes = ["All"] + [n['naics_2'] for n in filter_opts.get('naics_codes', [])]
        selected_naics = st.selectbox("NAICS (2-digit)", naics_codes, index=0)
    else:
        selected_category = "All"
        selected_naics = "All"
        st.warning("Filter options not loaded")

    st.header("Map Settings")
    color_scale = st.slider("Color intensity", 0.05, 0.5, 0.15, 0.01,
                           help="Excess lean value for full color saturation")
    point_radius = st.slider("Point size", 50, 500, 150, 10)
    sample_size = st.slider("Max points", 10000, 100000, 50000, 5000,
                           help="Sample size for performance")

    st.header("View Presets")
    preset = st.radio("Quick zoom", ["US Overview", "California", "New York", "Texas", "Florida"])

    preset_views = {
        "US Overview": (39.8, -98.5, 4),
        "California": (36.7, -119.4, 6),
        "New York": (40.7, -74.0, 10),
        "Texas": (31.0, -100.0, 6),
        "Florida": (27.8, -81.7, 6),
    }


df = get_sampled_data(selected_category, selected_naics, sample_size)

if df is None:
    st.error("Data not available. Please wait for data preparation to complete.")
    st.stop()

if len(df) == 0:
    st.warning("No POIs match the current filters.")
    st.stop()

st.info(f"Showing {len(df):,} POIs (sampled from full dataset)")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("POIs Displayed", f"{len(df):,}")
with col2:
    st.metric("Unique Brands", f"{df['brand'].nunique():,}")
with col3:
    mean_lean = df['mean_rep_lean_2020'].mean()
    st.metric("Mean Rep Lean", f"{mean_lean:.3f}" if pd.notna(mean_lean) else "N/A")
with col4:
    std_lean = df['mean_rep_lean_2020'].std()
    st.metric("Std Dev", f"{std_lean:.3f}" if pd.notna(std_lean) else "N/A")

center_lat, center_lon, zoom = preset_views[preset]
view_state = create_map_view(center_lat, center_lon, zoom)

try:
    map_df = df.copy()

    if 'location_name' in map_df.columns:
        map_df['display_name'] = map_df['location_name'].fillna('Unknown')
    else:
        map_df['display_name'] = map_df['brand'].fillna(map_df['top_category'].fillna('Unknown'))

    def format_brand(brand):
        if pd.isna(brand) or brand == 'Unbranded' or brand == '':
            return ''
        return f'<b>Brand:</b> {brand}<br/>'
    map_df['brand_display'] = map_df['brand'].apply(format_brand)

    map_df['lean_display'] = map_df['mean_rep_lean_2020'].apply(
        lambda x: f'{x:.3f}' if pd.notna(x) else 'N/A'
    )
    map_df['visitors_display'] = map_df['total_visitors'].apply(
        lambda x: f'{int(x):,}' if pd.notna(x) else 'N/A'
    )

    layer = create_scatter_layer(map_df, color_column='mean_rep_lean_2020', scale=color_scale,
                                radius=point_radius, size_by_visitors=True)
    tooltip = create_tooltip()
    deck = create_deck([layer], view_state, tooltip)
    st.pydeck_chart(deck, use_container_width=True)
except Exception as e:
    st.error(f"Error rendering map: {e}")
    st.write("Falling back to simple map...")
    st.map(df[['latitude', 'longitude']].dropna().head(10000))

st.markdown("---")

st.subheader("Legend")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("🔴 **Red**: Republican-leaning customers (>0.5)")
with col2:
    st.markdown("⚪ **Gray/White**: Neutral (~0.5)")
with col3:
    st.markdown("🔵 **Blue**: Democratic-leaning customers (<0.5)")

st.markdown("---")

st.subheader("Sample Data")
with st.expander("Show data table"):
    display_cols = ['brand', 'city', 'region', 'mean_rep_lean_2020',
                   'total_visitors', 'top_category', 'naics_code']
    display_df = df[display_cols].sort_values('mean_rep_lean_2020', ascending=False).head(100)
    st.dataframe(display_df.round(3), width="stretch")
