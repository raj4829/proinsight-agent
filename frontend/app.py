import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
import json

# ---------- Frontend Configuration ----------
st.set_page_config(page_title="ProInsight SaaS Platform", layout="wide", page_icon="🚀")

BACKEND_URL = "http://localhost:8000/v1/agent/analyze"

CUSTOM_CSS = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto+Mono:wght@500;700&display=swap');
    
    :root {
        --primary: #0EA5E9;
        --secondary: #0F172A;
        --accent: #10B981;
        --bg: #0B0E14;
        --surface: #161B22;
        --border: #30363D;
        --text: #F0F6FC;
        --text-muted: #8B949E;
    }

    .stApp { 
        background-color: var(--bg);
        color: var(--text); 
        font-family: 'Inter', sans-serif; 
    }
    
    .stSidebar { 
        background-color: var(--secondary);
        border-right: 1px solid var(--border);
    }

    h1 { 
        font-family: 'Inter', sans-serif;
        background: linear-gradient(90deg, #0EA5E9 0%, #38BDF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem;
        letter-spacing: -0.02em;
    }

    .metric-card {
        background: var(--surface);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--border);
        transition: all 0.2s ease;
        height: 100%;
    }
    
    .metric-value {
        font-family: 'Roboto Mono', monospace;
        font-size: 2.25rem;
        font-weight: 700;
        color: var(--primary);
    }

    .insight-box {
        background: var(--surface);
        border-left: 4px solid var(--primary);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    </style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------- State Management ----------
if "session_id" not in st.session_state:
    st.session_state["session_id"] = datetime.now().strftime("%Y%m%d%H%M%S")
if "query_history" not in st.session_state:
    st.session_state["query_history"] = []

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### 🏛️ ProInsight SaaS")
    st.caption("v3.1 Client-Server Architecture")
    st.markdown("---")
    
    api_key = st.text_input("OpenAI API Key", type="password")
    
    st.markdown("---")
    st.info("Backend: FastAPI on :8000")
    st.info("Database: Persistent MotherDuck / analytics.db")

# ---------- Main UI ----------
st.markdown("# 🚀 ProInsight SaaS Architecture")
st.markdown("*Decoupled Client-Server Platform for 100K+ Scale*")
st.markdown("---")

tab_query, tab_logs = st.tabs(["💬 Dynamic Query", "📜 Activity Logs"])

with tab_query:
    query = st.text_area("Ask the Agent Team:", height=150, placeholder="e.g., 'What is our total revenue growth by channel?'")
    
    if st.button("🚀 Consult Agent Team", type="primary", use_container_width=True):
        if not api_key:
            st.error("Please provide an OpenAI API Key in the sidebar.")
        else:
            with st.spinner("🧠 Requesting Backend Analysis..."):
                try:
                    payload = {
                        "query": query,
                        "session_id": st.session_state["session_id"],
                        "api_key": api_key
                    }
                    response = requests.post(BACKEND_URL, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.markdown("### 🏛️ Executive Briefing")
                        st.markdown(data["answer"])
                        
                        if data["sql"]:
                            with st.expander("📝 Derived SQL Logic"):
                                st.code(data["sql"], language="sql")
                        
                        st.session_state["query_history"].append({
                            "query": query,
                            "timestamp": datetime.now().strftime("%H:%M:%S")
                        })
                    else:
                        st.error(f"Backend Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection Failed: {e}")

with tab_logs:
    if st.session_state["query_history"]:
        for item in reversed(st.session_state["query_history"]):
            st.markdown(f"**[{item['timestamp']}]** {item['query']}")
    else:
        st.info("No queries recorded in this session.")
