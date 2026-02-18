import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
import json
import time

# ---------- Elite SaaS Design System (v3.2) ----------
st.set_page_config(page_title="ProInsight SaaS Elite", layout="wide", page_icon="🏛️")

BACKEND_URL = "http://localhost:8000"

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

    .stApp { background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; }
    .stSidebar { background-color: var(--secondary); border-right: 1px solid var(--border); }
    
    h1 { 
        background: linear-gradient(90deg, #0EA5E9 0%, #38BDF8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 2.8rem; letter-spacing: -0.02em;
    }
    
    .metric-card {
        background: var(--surface); border-radius: 12px; padding: 1.5rem;
        border: 1px solid var(--border); transition: all 0.2s ease;
        margin-bottom: 1rem;
    }
    .metric-card:hover { border-color: var(--primary); transform: translateY(-2px); box-shadow: 0 0 20px rgba(14, 165, 233, 0.1); }
    .metric-value { font-family: 'Roboto Mono', monospace; font-size: 2rem; font-weight: 700; color: var(--primary); }
    .metric-label { font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; letter-spacing: 0.1em; }

    .insight-box {
        background: var(--surface); border-left: 4px solid var(--primary);
        padding: 1.5rem; border-radius: 12px; margin: 1rem 0;
        border-top: 1px solid var(--border); border-right: 1px solid var(--border); border-bottom: 1px solid var(--border);
    }
    
    .thought-step {
        color: var(--accent); font-family: 'Roboto Mono', monospace; font-size: 0.85rem; padding: 4px 0;
    }
    </style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------- State Initialization ----------
if "api_key" not in st.session_state: st.session_state["api_key"] = ""
if "query_log" not in st.session_state: st.session_state["query_log"] = []

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🏛️ ProInsight SaaS")
    st.caption("Decoupled Enterprise Architecture")
    st.markdown("---")
    
    st.session_state["api_key"] = st.text_input("SaaS AI Gateway (OpenAI Key)", type="password", value=st.session_state["api_key"])
    
    st.markdown("### ☁️ Cloud Ingestion")
    uploaded_file = st.file_uploader("Upload CSV Stream", type=["csv"])
    if uploaded_file:
        if st.button("🚀 Push to SaaS DB", use_container_width=True):
            with st.spinner("Streaming to FastAPI..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                res = requests.post(f"{BACKEND_URL}/v1/data/upload", files=files)
                if res.status_code == 200:
                    st.success(f"Ingested {res.json()['rows']} rows into cloud storage.")
                else:
                    st.error("Ingestion failed. Ensure backend is running.")

    st.markdown("---")
    st.caption("v3.2.1 | Client: Streamlit | Server: FastAPI")

# ---------- Main SaaS Interface ----------
st.markdown("# 🚀 ProInsight SaaS")
st.markdown("*Premium Executive Intelligence & AI Team Synthesis*")
st.markdown("---")

tab_query, tab_strategy, tab_reports, tab_manage = st.tabs([
    "💬 AI Team Consultation", "🎯 Strategy Hub", "📑 Enterprise Reports", "🛠️ System Status"
])

with tab_strategy:
    st.markdown("### 🎯 Strategic Channel Hub")
    st.markdown("*Real-time comparative analysis of marketing efficiency across multiple data streams.*")
    
    if st.button("📈 Run Comparative Analysis", use_container_width=True):
        try:
            res = requests.get(f"{BACKEND_URL}/v1/analytics/comparative")
            if res.status_code == 200:
                data = res.json()["data"]
                if data:
                    df_comp = pd.DataFrame(data)
                    
                    # 1. Visualization
                    fig = px.bar(df_comp, x="channel", y="roas", 
                                color="roi", text="roas",
                                title="Marketing Efficiency by Channel (ROAS vs ROI)",
                                template="plotly_dark",
                                color_continuous_scale="Viridis")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 2. Winning Channels Grid
                    st.markdown("#### 🏆 Top Performing Channels")
                    cols = st.columns(len(data))
                    for i, item in enumerate(data):
                        with cols[i]:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">{item['channel']}</div>
                                <div class="metric-value">{item['roas']}x</div>
                                <div style="color: var(--accent); font-size: 0.9rem;">ROI: {item['roi']}%</div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # 3. AI Winning Insights
                    winning_channel = df_comp.loc[df_comp['roas'].idxmax()]['channel']
                    st.markdown(f"""
                    <div class="insight-box" style="border-left-color: var(--accent);">
                        <strong>🏆 Winning Strategy Identified</strong><br>
                        The AI agent has identified <b>{winning_channel}</b> as your most efficient scale-up point with a ROAS of 
                        <b>{df_comp['roas'].max()}x</b>. Reallocating budget from underperforming channels is recommended for 
                        immediate ROI acceleration.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("No comparable marketing data (Revenue + Cost) found in current tables.")
            else:
                st.error("Backend failed to process analysis.")
        except Exception as e:
            st.error(f"Analysis failed: {e}")

with tab_query:
    col_in, col_out = st.columns([1, 2])
    
    with col_in:
        st.markdown("#### 💬 Consult AI Team")
        query = st.text_area("Ask for strategic analysis:", height=200, placeholder="e.g., 'Analyze our marketing efficiency and find external benchmarks for SaaS ROAS.'")
        
        if st.button("🚀 Consult Supervisor", type="primary", use_container_width=True):
            if not st.session_state["api_key"]:
                st.warning("⚠️ Please provide an API key in the sidebar.")
            else:
                with st.spinner("🧠 Supervisor is orchestrating the team..."):
                    payload = {"query": query, "api_key": st.session_state["api_key"]}
                    try:
                        # Visualization of thought process
                        thought_container = st.empty()
                        steps = ["Initializing Team...", "Analyst pulling DuckDB data...", "Researcher deep-diving web...", "Supervisor synthesizing briefing..."]
                        for s in steps:
                            thought_container.markdown(f"📡 <span class='thought-step'>{s}</span>", unsafe_allow_html=True)
                            time.sleep(0.5)
                        
                        start_time = time.time()
                        res = requests.post(f"{BACKEND_URL}/v1/agent/analyze", json=payload)
                        elapsed = time.time() - start_time
                        
                        if res.status_code == 200:
                            data = res.json()
                            with col_out:
                                st.markdown("### 🏛️ Executive Intelligence Briefing")
                                st.markdown(data["answer"])
                                
                                if data["sql"]:
                                    with st.expander("📝 Strategic SQL Engine"):
                                        st.code(data["sql"], language="sql")
                                
                                st.caption(f"Analysis completed in {elapsed:.2f}s | Source: SaaS Core")
                                st.session_state["query_log"].append({"q": query, "t": datetime.now().strftime("%H:%M")})
                        else:
                            st.error(f"SaaS Core Error: {res.text}")
                    except Exception as e:
                        st.error(f"❌ Connection to SaaS Core failed: {e}")
    
    with col_out:
        if not st.session_state["query_log"]:
            st.info("💡 Enter a query to begin. The Supervisor will coordinate multiple specialized agents to build your report.")
        
with tab_reports:
    st.markdown("### 📑 Enterprise Report Archive")
    if st.session_state["query_log"]:
        for item in reversed(st.session_state["query_log"]):
            st.markdown(f"""
            <div class="insight-box">
                <strong>{item['t']} | Strategic Inquiry</strong><br>
                {item['q']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No reports generated in this session.")

with tab_manage:
    st.markdown("### 🛠️ SaaS System Monitoring")
    col1, col2, col3 = st.columns(3)
    col1.metric("API Protocol", "REST / JSON")
    col2.metric("Worker Node", "Local-Host")
    col3.metric("DB Engine", "DuckDB (Persistent)")
    
    st.markdown("---")
    st.markdown("#### 🧠 Ralph/GSD Architecture Protocol")
    st.code("""
    {
        "governance": "Supervisor-Led Trio",
        "orchestration": "Agno Team Framework",
        "persistence": "MotherDuck / DuckDB",
        "saas_scaling": "Decoupled FastAPI Client-Server"
    }
    """, language="json")
