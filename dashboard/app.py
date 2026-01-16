"""
Measuring Stakeholder Ideology - Interactive Dashboard

Main entry point for the Streamlit multi-page application.

Run locally:
    streamlit run app.py

Run on Savio with SSH tunnel:
    1. On Savio: streamlit run app.py --server.port 8501 --server.address 0.0.0.0
    2. On laptop: ssh -L 8501:localhost:8501 maxkagan@hpc.brc.berkeley.edu
    3. Open: http://localhost:8501
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.data_loader import check_data_available

st.set_page_config(
    page_title="Stakeholder Ideology Explorer",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🗳️ Measuring Stakeholder Ideology")
    st.markdown("**Interactive explorer for consumer partisan lean across brands and locations**")

    data_ready, missing_files = check_data_available()

    if not data_ready:
        st.error("Dashboard data is not yet available.")
        st.warning(f"Missing files: {', '.join(missing_files)}")
        st.info("""
        **Data preparation is in progress.**

        The dashboard requires pre-computed data files. If you just submitted the data prep job,
        please wait for it to complete (check with `squeue -u maxkagan`).

        Expected data location: `/global/scratch/users/maxkagan/measuring_stakeholder_ideology/dashboard_data/`
        """)

        with st.expander("Show expected files"):
            st.markdown("""
            - `poi_with_coords.parquet` - POI data with coordinates and partisan lean
            - `brand_summary.parquet` - Brand-level aggregate statistics
            - `msa_summary.parquet` - MSA-level aggregate statistics
            - `filter_options.json` - Available categories and NAICS codes
            """)
        return

    st.success("Dashboard data loaded successfully!")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🗺️ Neighbor Map")
        st.markdown("""
        Interactive map showing POIs colored by **excess partisan lean**
        (deviation from local neighbors).

        Filter by category or NAICS code to compare like businesses.
        """)
        if st.button("Open Neighbor Map", key="btn_map"):
            st.switch_page("pages/1_neighbor_map.py")

    with col2:
        st.markdown("### 🏢 Brand Explorer")
        st.markdown("""
        Search and compare brands by partisan lean.

        See which brands attract the most/least Republican customers
        and how much variation exists across locations.
        """)
        if st.button("Open Brand Explorer", key="btn_brand"):
            st.switch_page("pages/2_brand_explorer.py")

    with col3:
        st.markdown("### 🌆 MSA Analysis")
        st.markdown("""
        Explore partisan lean by metropolitan area.

        Compare brands within the same MSA to see
        local variation in customer bases.
        """)
        if st.button("Open MSA Analysis", key="btn_msa"):
            st.switch_page("pages/3_msa_analysis.py")

    st.markdown("---")

    st.markdown("### About This Dashboard")
    st.markdown("""
    This dashboard visualizes **consumer partisan lean** for millions of U.S. points of interest,
    derived from foot traffic data and CBG-level election results.

    **Key insight**: The map shows **excess partisan lean** - how much more Republican/Democratic
    a location's customers are compared to nearby businesses in the same category. This reveals
    brand-specific effects beyond simple geography.

    **Data sources**:
    - Advan foot traffic data (visitor home CBGs)
    - 2020 Presidential election results (CBG-level)
    """)


if __name__ == "__main__":
    main()
