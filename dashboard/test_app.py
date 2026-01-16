"""
Minimal test dashboard to verify SSH tunneling works.
No data dependencies - just tests that Streamlit runs and is accessible.
"""

import streamlit as st

st.set_page_config(page_title="Test Dashboard", page_icon="🧪", layout="wide")

st.title("🧪 SSH Tunnel Test")
st.success("If you can see this, the SSH tunnel is working!")

st.markdown("---")

st.subheader("Interactive Test")
name = st.text_input("Enter your name:", "Max")
st.write(f"Hello, {name}!")

slider_val = st.slider("Pick a number:", 0, 100, 50)
st.write(f"You picked: {slider_val}")

st.markdown("---")

st.subheader("System Info")
import socket
st.code(f"Running on: {socket.gethostname()}")

st.markdown("---")
st.info("Close this with Ctrl+C in the terminal when done testing.")
