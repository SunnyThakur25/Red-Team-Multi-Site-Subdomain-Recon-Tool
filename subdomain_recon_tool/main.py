# main.py
import streamlit as st
from recon import run_red_team_scan
from utils import load_logo, load_keywords
import os
import asyncio

# Setting up eye-catching Streamlit page
st.set_page_config(page_title="Red Team Multi-Site Recon", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for vibrant GUI
st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #1a1a2e, #16213e); color: #e0e0e0; }
        .stTextInput > div > div > input { background-color: #2a2a4a; color: #e0e0e0; border: 2px solid #ff4b4b; border-radius: 5px; }
        .stButton > button { background: linear-gradient(45deg, #ff4b4b, #ff7878); color: white; border: none; border-radius: 5px; padding: 10px 20px; font-weight: bold; }
        .stButton > button:hover { background: linear-gradient(45deg, #ff7878, #ff4b4b); }
        .sidebar .stImage { border: 3px solid #00d4ff; border-radius: 10px; }
        .stExpander { background-color: #2a2a4a; border: 1px solid #00d4ff; border-radius: 5px; }
        h1, h2, h3 { color: #00d4ff; text-shadow: 1px 1px 2px #ff4b4b; }
    </style>
""", unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.image(load_logo("assets/logo.png"), width=200)
    st.title("Recon Controls")
    domains_input = st.text_area("Target Domains (one per line, e.g., example.com):", "")
    output_dir = st.text_input("Output Directory:", "screenshots")
    wordlist_file = st.text_input("Subdomain Wordlist Path:", "wordlists/subdomains.txt")
    keyword_file = st.text_input("Keyword Wordlist Path:", "wordlists/keywords.txt")
    st.markdown("---")
    st.subheader("Visual Settings")
    theme = st.selectbox("Theme", ["Dark Gradient", "Cyber Neon"])
    if theme == "Cyber Neon":
        st.markdown("""
            <style>
                .stApp { background: linear-gradient(135deg, #0f0c29, #302b63); }
                .stTextInput > div > div > input { border: 2px solid #00ffcc; }
                .stButton > button { background: linear-gradient(45deg, #00ffcc, #ff00ff); }
                .stButton > button:hover { background: linear-gradient(45deg, #ff00ff, #00ffcc); }
            </style>
        """, unsafe_allow_html=True)

# Main page
col1, col2 = st.columns([1, 3])
with col1:
    st.image(load_logo("assets/logo.png"), width=150)
with col2:
    st.title("Red Team Multi-Site Subdomain Recon Tool")
    st.markdown("**Discover subdomains across multiple websites, classify pages, and capture screenshots!**")

# Run button
if st.button("Launch Recon", key="run_button", help="Start multi-site subdomain scan"):
    if not domains_input:
        st.error("Please enter at least one domain!")
    else:
        domains = [d.strip() for d in domains_input.split("\n") if d.strip()]
        with st.spinner("Scanning subdomains and capturing screenshots..."):
            keywords = load_keywords(keyword_file)
            # Run the async function in a synchronous context
            results = asyncio.run(run_red_team_scan(domains, output_dir, wordlist_file, keywords))
        
        # Displaying results
        st.header("Scan Results")
        for domain, domain_results in results.items():
            st.markdown(f"### Domain: {domain}")
            for subdomain, data in domain_results.items():
                with st.expander(f"Subdomain: {subdomain}", expanded=True):
                    st.markdown(f"**URL:** {data['url']}")
                    st.markdown(f"**Category:** {data['category']}")
                    if data['screenshot']:
                        st.image(data['screenshot'], caption=f"Screenshot: {subdomain}", width=500)
                    st.markdown(f"**Passive Source:** {data['passive_source']}")
                    st.markdown("---")