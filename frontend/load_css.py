import streamlit as st
import os

def load_css():
    """Load the custom CSS file."""
    css_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css")
    
    with open(css_file, "r") as f:
        css = f.read()
        
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)