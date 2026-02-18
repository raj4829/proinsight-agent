import streamlit as st
import pandas as pd
import duckdb
import re
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from fpdf import FPDF
import unicodedata
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime
import base64

# ---------- Configuration ----------
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

    h2, h3 { 
        color: var(--primary); 
        font-weight: 600;
        letter-spacing: -0.01em;
    }

    .stButton>button { 
        background: var(--primary);
        color: white; 
        border-radius: 8px; 
        font-weight: 600;
        border: none;
        padding: 0.6rem 1.5rem;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer !important;
    }

    .stButton>button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
    }

    .stTextInput>div>div>input { 
        border-radius: 8px;
        border: 1px solid var(--border);
        background: var(--surface);
        color: var(--text);
    }

    /* Bento Grid Metric Cards */
    .metric-card {
        background: var(--surface);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--border);
        transition: all 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-card:hover {
        border-color: var(--primary);
        box-shadow: 0 0 20px rgba(14, 165, 233, 0.1);
        transform: translateY(-2px);
    }

    .metric-value {
        font-family: 'Roboto Mono', monospace;
        font-size: 2.25rem;
        font-weight: 700;
        color: var(--primary);
        line-height: 1.1;
        margin: 0.5rem 0;
        word-break: break-all;
    }

    .metric-label {
        font-size: 0.8rem;
        color: var(--text-muted);
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.05em;
    }

    .insight-box {
        background: var(--surface);
        border: 1px solid var(--border);
        border-left: 4px solid var(--primary);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        font-size: 1rem;
        line-height: 1.7;
        color: var(--text);
        word-wrap: break-word;
        overflow-wrap: break-word;
        word-break: keep-all;
    }
    
    .insight-box strong {
        color: var(--primary);
        display: block;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px;
        color: var(--text-muted);
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        color: var(--primary) !important;
        border-bottom-color: var(--primary) !important;
    }

    /* Mobile Responsiveness */
    @media (max-width: 600px) {
        h1 { font-size: 2rem !important; }
        .metric-value { font-size: 2rem !important; }
        .stButton>button { width: 100%; }
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
    }
    </style>
"""

# ---------- Utilities ----------
def ensure_state():
    """Initialize session state variables."""
    keys = {
        "duckdb_con": None,
        "datasets": {},
        "openai_key": None,
        "agent": None,
        "last_result": None,
        "query_history": [],
        "insights_cache": {},
    }
    for k, v in keys.items():
        if k not in st.session_state:
            st.session_state[k] = v

def get_duckdb_con():
    if st.session_state.get("duckdb_con") is None:
        st.session_state["duckdb_con"] = duckdb.connect(database=":memory:")
    return st.session_state["duckdb_con"]

def register_dataset(name: str, df: pd.DataFrame):
    con = get_duckdb_con()
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', name).lower()
    try:
        con.register(safe_name, df)
        st.session_state["datasets"][safe_name] = df
        return safe_name
    except Exception as e:
        st.error(f"Error registering {name}: {e}")
        return None

def run_sql(sql: str) -> pd.DataFrame:
    con = get_duckdb_con()
    if not sql: return pd.DataFrame()
    try:
        return con.execute(sql).df()
    except Exception as e:
        raise RuntimeError(f"SQL Error: {e}")

def extract_sql_from_text(text: str) -> str:
    if not text: return ""
    blocks = re.findall(r"```(?:sql)?\s*([\s\S]*?)```", text, flags=re.IGNORECASE)
    if blocks: return blocks[0].strip()
    return ""

def calculate_advanced_metrics(datasets):
    """Enhanced metrics calculation with business intelligence."""
    metrics = {}
    all_data = pd.concat(datasets.values(), ignore_index=True) if datasets else pd.DataFrame()
    
    for name, df in datasets.items():
        # Volume Metrics
        metrics[f"{name}_records"] = len(df)
        
        # Financial Metrics
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            c = col.lower()
            if any(x in c for x in ['revenue', 'sales']):
                total = df[col].sum()
                avg = df[col].mean()
                metrics[f"{name}_total_{col}"] = total
                metrics[f"{name}_avg_{col}"] = avg
                # Growth rate if date column exists
                date_cols = df.select_dtypes(include=['datetime']).columns
                if len(date_cols) > 0:
                    df_sorted = df.sort_values(date_cols[0])
                    if len(df_sorted) > 1:
                        first_val = df_sorted[col].iloc[0]
                        last_val = df_sorted[col].iloc[-1]
                        if first_val > 0:
                            growth = ((last_val - first_val) / first_val) * 100
                            metrics[f"{name}_{col}_growth_pct"] = growth
                            
            elif any(x in c for x in ['cost', 'spend', 'budget']):
                total = df[col].sum()
                metrics[f"{name}_total_{col}"] = total
                
            elif 'units' in c or 'quantity' in c:
                total = df[col].sum()
                metrics[f"{name}_total_{col}"] = total
    
    # Cross-dataset calculations (ROI, ROAS, etc.)
    if len(datasets) >= 2:
        # Try to calculate ROI/ROAS if we have revenue and spend data
        revenue_total = sum([v for k, v in metrics.items() if 'revenue' in k.lower() and 'total' in k])
        spend_total = sum([v for k, v in metrics.items() if 'spend' in k.lower() and 'total' in k])
        
        if spend_total > 0 and revenue_total > 0:
            metrics['calculated_roas'] = revenue_total / spend_total
            metrics['calculated_roi_pct'] = ((revenue_total - spend_total) / spend_total) * 100
    
    return metrics

def format_metric_value(key, value):
    """Smart formatting for different metric types."""
    if isinstance(value, (int, float)):
        if 'pct' in key or 'growth' in key:
            return f"{value:+.1f}%"
        elif any(x in key for x in ['revenue', 'cost', 'spend', 'profit']):
            return f"${value:,.0f}"
        elif 'roas' in key or 'roi' in key:
            if 'pct' in key:
                return f"{value:.1f}%"
            else:
                return f"{value:.2f}x"
        elif 'records' in key or 'total' in key:
            return f"{int(value):,}"
        else:
            return f"{value:,.2f}"
    return str(value)

# ---------- Advanced Visualization ----------
def create_advanced_chart(df: pd.DataFrame, chart_type="auto"):
    """Enhanced visualization with multiple chart types."""
    if df.empty: return None
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    
    # Auto-detect best chart type
    if chart_type == "auto":
        if date_cols and numeric_cols:
            chart_type = "line"
        elif cat_cols and numeric_cols:
            chart_type = "bar"
        elif len(numeric_cols) >= 2:
            chart_type = "scatter"
    
    # Create chart based on type
    if chart_type == "line" and date_cols and numeric_cols:
        x_col, y_col = date_cols[0], numeric_cols[0]
        fig = px.line(df, x=x_col, y=y_col, 
                     title=f"{y_col} Trend Analysis",
                     template="plotly_dark")
        fig.update_traces(line=dict(color='#4F8BF9', width=3))
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", size=12, color="#fafafa"),
            title_font=dict(size=20, color="#4F8BF9"),
            hovermode='x unified'
        )
        return fig
        
    elif chart_type == "bar" and cat_cols and numeric_cols:
        x_col, y_col = cat_cols[0], numeric_cols[0]
        if len(df) > 20: df = df.nlargest(20, y_col)
        fig = px.bar(df, x=x_col, y=y_col,
                    title=f"Top {min(len(df), 20)} by {y_col}",
                    template="plotly_dark")
        fig.update_traces(marker=dict(color='#4F8BF9', 
                                      line=dict(color='#7B68EE', width=2)))
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", size=12, color="#fafafa"),
            title_font=dict(size=20, color="#4F8BF9")
        )
        return fig
        
    elif chart_type == "scatter" and len(numeric_cols) >= 2:
        fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                        title=f"{numeric_cols[0]} vs {numeric_cols[1]}",
                        template="plotly_dark",
                        trendline="ols")
        fig.update_traces(marker=dict(size=10, color='#4F8BF9', 
                                      line=dict(color='#7B68EE', width=1)))
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", size=12, color="#fafafa"),
            title_font=dict(size=20, color="#4F8BF9")
        )
        return fig
    
    return None

def run_forecast(df: pd.DataFrame, periods=30):
    """Enhanced forecasting with confidence intervals."""
    date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if not date_cols or not numeric_cols:
        return None, "Need at least one Date column and one Numeric column."
        
    date_col, val_col = date_cols[0], numeric_cols[0]
    df = df.sort_values(date_col)
    df['ordinal_date'] = df[date_col].map(pd.Timestamp.toordinal)
    
    X = df[['ordinal_date']]
    y = df[val_col]
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Calculate confidence intervals
    predictions_train = model.predict(X)
    residuals = y - predictions_train
    std_error = np.std(residuals)
    
    last_date = df[date_col].max()
    future_dates = [last_date + pd.Timedelta(days=x) for x in range(1, periods + 1)]
    future_ordinal = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
    predictions = model.predict(future_ordinal)
    
    # Create forecast with confidence bands
    forecast_df = pd.DataFrame({
        date_col: future_dates,
        val_col: predictions,
        'lower_bound': predictions - (1.96 * std_error),
        'upper_bound': predictions + (1.96 * std_error),
        'type': 'Forecast'
    })
    
    df['type'] = 'Actual'
    df['lower_bound'] = df[val_col]
    df['upper_bound'] = df[val_col]
    
    combined = pd.concat([df[[date_col, val_col, 'type', 'lower_bound', 'upper_bound']], forecast_df])
    
    # Calculate forecast metrics
    trend = "upward" if predictions[-1] > predictions[0] else "downward"
    avg_change = (predictions[-1] - predictions[0]) / periods
    
    message = f"Forecasted {val_col} for next {periods} days. Trend: {trend} ({avg_change:+.2f} per day)"
    
    return combined, message

# ---------- Enhanced PDF Reporting ----------
def create_executive_pdf(client_name, report_data, chart_image=None):
    """Premium PDF report with enhanced formatting."""
    pdf = FPDF()
    pdf.add_page()
    
    # Header with gradient effect (simulated with colors)
    pdf.set_fill_color(14, 17, 23)
    pdf.rect(0, 0, 210, 50, 'F')
    
    # Title
    pdf.set_font("Arial", 'B', 28)
    pdf.set_text_color(79, 139, 249)
    pdf.set_xy(10, 15)
    pdf.cell(0, 12, "EXECUTIVE INTELLIGENCE REPORT", 0, 1, 'C')
    
    # Subtitle
    pdf.set_font("Arial", 'I', 14)
    pdf.set_text_color(139, 146, 167)
    pdf.cell(0, 8, f"Prepared for {client_name}", 0, 1, 'C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 0, 1, 'C')
    
    pdf.ln(15)
    
    def safe_text(text):
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    
    # Executive Summary Box
    pdf.set_fill_color(30, 33, 48)
    pdf.set_draw_color(79, 139, 249)
    pdf.set_line_width(0.5)
    pdf.rect(10, pdf.get_y(), 190, 10, 'DF')
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(79, 139, 249)
    pdf.cell(0, 10, "  EXECUTIVE SUMMARY", 0, 1, 'L')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 11)
    summary_text = safe_text(report_data.get('summary', 'No summary available.'))
    pdf.multi_cell(0, 6, summary_text)
    pdf.ln(8)
    
    # Key Performance Indicators
    if report_data.get('kpis'):
        pdf.set_fill_color(30, 33, 48)
        pdf.rect(10, pdf.get_y(), 190, 10, 'DF')
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(79, 139, 249)
        pdf.cell(0, 10, "  KEY PERFORMANCE INDICATORS", 0, 1, 'L')
        pdf.ln(2)
        
        pdf.set_font("Courier", 'B', 10)
        pdf.set_text_color(0, 0, 0)
        
        kpis = report_data['kpis']
        # Display KPIs in a grid
        col_width = 90
        row_height = 8
        i = 0
        for k, v in kpis.items():
            formatted_val = format_metric_value(k, v) if isinstance(v, (int, float)) else str(v)
            text = safe_text(f"{k}: {formatted_val}")
            pdf.cell(col_width, row_height, text, 0, 0)
            i += 1
            if i % 2 == 0: 
                pdf.ln(row_height)
        if i % 2 != 0:
            pdf.ln(row_height)
        pdf.ln(8)
    
    # Strategic Insights
    pdf.set_fill_color(30, 33, 48)
    pdf.rect(10, pdf.get_y(), 190, 10, 'DF')
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(79, 139, 249)
    pdf.cell(0, 10, "  STRATEGIC INSIGHTS", 0, 1, 'L')
    
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(0, 0, 0)
    insights_text = safe_text(report_data.get('insights', 'No insights available.'))
    pdf.multi_cell(0, 6, insights_text)
    pdf.ln(8)
    
    # Recommendations
    pdf.set_fill_color(30, 33, 48)
    pdf.rect(10, pdf.get_y(), 190, 10, 'DF')
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(79, 139, 249)
    pdf.cell(0, 10, "  ACTION RECOMMENDATIONS", 0, 1, 'L')
    
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(0, 0, 0)
    recs_text = safe_text(report_data.get('recommendations', 'No recommendations available.'))
    pdf.multi_cell(0, 6, recs_text)
    
    # Footer
    pdf.set_y(-20)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(139, 146, 167)
    pdf.cell(0, 10, "ProInsight Agency Platform | Powered by AI & Advanced Analytics", 0, 0, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# ---------- UI Layout ----------
st.set_page_config(page_title="ProInsight Agency Platform", layout="wide", page_icon="🚀")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
ensure_state()

# Sidebar
with st.sidebar:
    st.markdown("### 🚀 ProInsight Agency")
    st.markdown("*Advanced Analytics Platform*")
    st.markdown("---")
    
    api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")
    if api_key: st.session_state["openai_key"] = api_key
        
    st.markdown("---")
    st.markdown("### 📂 Data Sources")
    uploaded_files = st.file_uploader("Upload Tables", accept_multiple_files=True, type=["csv", "xlsx"],
                                     help="Upload CSV or Excel files for analysis")
    
    if uploaded_files:
        for file in uploaded_files:
            file_name = file.name.split('.')[0]
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', file_name).lower()
            if clean_name not in st.session_state["datasets"]:
                if file.name.endswith('.csv'): df = pd.read_csv(file)
                else: df = pd.read_excel(file)
                for col in df.columns:
                    if "date" in col.lower() or "time" in col.lower():
                        try: df[col] = pd.to_datetime(df[col])
                        except: pass
                if register_dataset(file_name, df): 
                    st.success(f"✓ Loaded: {clean_name}")

    if st.session_state["datasets"]:
        st.markdown("### 📚 Active Tables")
        for name, data in st.session_state["datasets"].items():
            with st.expander(f"📊 {name}"):
                st.caption(f"**Rows:** {len(data):,}")
                st.caption(f"**Columns:** {', '.join(data.columns[:5])}" + ("..." if len(data.columns) > 5 else ""))
    
    st.markdown("---")
    if st.button("🔄 Reset Workspace", help="Clear all data and start fresh"):
        st.session_state.clear()
        st.rerun()

# Main Content
if not st.session_state.get("openai_key"):
    st.warning("⚠️ Please enter your OpenAI API Key in the sidebar to begin.")
    st.stop()

# Initialize Agent with Schema Awareness
datasets_hash = list(st.session_state["datasets"].keys())
if (st.session_state.get("agent") is None or 
    st.session_state.get("last_datasets_hash") != datasets_hash):
    
    schema_desc = "Available Tables:\n"
    for name, df in st.session_state["datasets"].items():
        cols_formatted = []
        for col in df.columns:
            if ' ' in col: cols_formatted.append(f'"{col}"')
            else: cols_formatted.append(col)
        schema_desc += f"- Table '{name}': Columns [{', '.join(cols_formatted)}]\n"
    
    st.session_state["agent"] = Agent(
        model=OpenAIChat(id="gpt-4o", api_key=st.session_state["openai_key"]),
        description="You are an elite Business Intelligence Consultant and DuckDB Expert.",
        instructions=[
            f"{schema_desc}",
            "Write optimized DuckDB SQL queries with proper aggregation.",
            "CAPABILITY BOUNDARY: You ONLY have access to the tables listed above. You CANNOT see future forecasts as tables.",
            "FORECASTING: If a user asks for 'forecasts', 'future predictions', or 'next 30 days', explain that these are generated in the specialized '🔮 Forecasting' tab using advanced trend modeling.",
            "JOIN LOGIC: You can join multiple tables using standard JOIN syntax.",
            "CRITICAL: Column names with spaces MUST be wrapped in double quotes (e.g., \"Units Sold\").",
            "Always wrap SQL in ```sql``` code blocks.",
            "Provide clear, professional explanations of query results in a consulting tone."
        ],
        markdown=True
    )
    st.session_state["last_datasets_hash"] = datasets_hash

agent = st.session_state["agent"]

# Header
st.markdown("# 🚀 ProInsight Agency Platform")
st.markdown("*Advanced AI-Powered Business Intelligence & Analytics*")
st.markdown("---")

# Tabs
tab_overview, tab_datalab, tab_query, tab_viz, tab_forecast, tab_report = st.tabs([
    "🏁 Executive Dashboard", "🔬 Data Lab", "💬 Deep Query", "📈 Interactive Viz", "🔮 Forecasting", "📑 Reports"
])

with tab_overview:
    if st.session_state["datasets"]:
        metrics = calculate_advanced_metrics(st.session_state["datasets"])
        
        # 1. High Level Hero Metrics (Bento Grid)
        st.markdown("### 🏛️ Executive Intelligence Hub")
        
        priority_metrics = {k: v for k, v in metrics.items() 
                          if any(x in k for x in ['total_revenue', 'total_cost', 'roas', 'roi', 'growth', 'calculated'])}
        
        if priority_metrics:
            m_list = list(priority_metrics.items())
            rows = [m_list[i:i + 4] for i in range(0, len(m_list), 4)]
            
            for row in rows:
                cols = st.columns(4)
                for idx, (key, value) in enumerate(row):
                    with cols[idx]:
                        label = key.replace('_', ' ').replace('calculated', 'AI').title()
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">{label}</div>
                            <div class="metric-value">{format_metric_value(key, value)}</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 2. Strategic Insights & Health Score
        col_health, col_insights = st.columns([1, 2])
        
        with col_health:
            st.markdown("#### 🛡️ Platform Health Score")
            health_score = 85 # Simulated base
            if 'calculated_roas' in metrics:
                health_score = min(100, int(85 + (metrics['calculated_roas'] * 2)))
            
            st.markdown(f"""
            <div style='text-align: center; padding: 2rem; background: var(--surface); border-radius: 12px; border: 1px solid var(--border);'>
                <div style='font-size: 4rem; font-weight: 800; color: var(--accent); line-height: 1;'>{health_score}</div>
                <div style='color: var(--text-muted); text-transform: uppercase; letter-spacing: 2px; margin-top: 1rem;'>Agency Reliability Score</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_insights:
            st.markdown("#### 💡 Strategic Insights")
            st.markdown(f"""
            <div class="insight-box">
                <strong>📈 Growth Momentum</strong><br>
                Your ecosystem identifies {len(st.session_state["datasets"])} primary data streams. 
                Current revenue velocity is trending {'positively' if health_score > 80 else 'stable'}.
            </div>
            <div class="insight-box">
                <strong>⚖️ Efficiency Core</strong><br>
                Data density has reached {sum(len(df) for df in st.session_state["datasets"].values()):,} points. 
                Focusing on high-margin channels is recommended based on current ROAS benchmarks.
            </div>
            """, unsafe_allow_html=True)

    else:
        st.info("📁 To begin, please upload your project datasets in the sidebar.")
        st.markdown("""
        ### ProInsight Starter Guide
        1. **Upload CSVs**: Drag your sales, marketing, or SaaS data.
        2. **Enter API Key**: Unlock GPT-4o powered deep reasoning.
        3. **Analyze**: Use the 'Deep Query' tab to ask business questions.
        """)

with tab_datalab:
    st.markdown("### 🔬 Data Laboratory")
    if st.session_state["datasets"]:
        selected_table = st.selectbox("Select Table to Explore", list(st.session_state["datasets"].keys()))
        df_lab = st.session_state["datasets"][selected_table]
        
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        col_stats1.metric("Rows", f"{len(df_lab):,}")
        col_stats2.metric("Columns", len(df_lab.columns))
        col_stats3.metric("Memory", f"{df_lab.memory_usage().sum() / 1024:.1f} KB")
        
        lab_sub1, lab_sub2, lab_sub3 = st.tabs(["📄 Preview", "📊 Distribution", "🛠️ Cleaning & Ops"])
        
        with lab_sub1:
            st.dataframe(df_lab, use_container_width=True)
        
        with lab_sub2:
            num_cols = df_lab.select_dtypes(include=['number']).columns
            if len(num_cols) > 0:
                scol = st.selectbox("Analyze Distribution of:", num_cols)
                
                # Optimized Plot with Marginals
                mean_val = df_lab[scol].mean()
                median_val = df_lab[scol].median()
                
                fig = px.histogram(
                    df_lab, 
                    x=scol, 
                    marginal="box",
                    template="plotly_dark", 
                    color_discrete_sequence=['#0EA5E9'],
                    title=f"Statistical Distribution: {scol}"
                )
                fig.add_vline(x=mean_val, line_dash="dash", line_color="#10B981", annotation_text="Mean")
                fig.add_vline(x=median_val, line_dash="dot", line_color="#F59E0B", annotation_text="Median")
                
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No numeric columns found for distribution analysis.")
        
        with lab_sub3:
            st.markdown("#### Meta-Analysis: Correlation Matrix")
            if st.button("📈 Run Correlation Analysis", use_container_width=True):
                num_df = df_lab.select_dtypes(include=['number'])
                if len(num_df.columns) > 1:
                    corr = num_df.corr()
                    fig = px.imshow(corr, text_auto=True, aspect="auto", 
                                   color_continuous_scale='RdBu_r', 
                                   template="plotly_dark",
                                   title="Variable Correlation Matrix")
                    st.plotly_chart(fig, use_container_width=True)
                    st.info("💡 Values closer to 1 or -1 indicate strong relationships.")
                else:
                    st.warning("Needs at least 2 numeric columns for correlation analysis.")
            
            st.markdown("---")
            st.markdown("#### Essential Data Operations")
            col_op1, col_op2 = st.columns(2)
            if col_op1.button("Drop Missing Values"):
                df_lab.dropna(inplace=True)
                st.success("Dropped missing rows.")
            if col_op2.button("Convert to Title Case"):
                cat_cols = df_lab.select_dtypes(include=['object']).columns
                for c in cat_cols:
                    df_lab[c] = df_lab[c].astype(str).str.title()
                st.success("Categorical columns titles optimized.")
            
            if st.button("🛡️ Remove Outliers (IQR)", use_container_width=True):
                num_cols = df_lab.select_dtypes(include=['number']).columns
                if len(num_cols) > 0:
                    initial_rows = len(df_lab)
                    for col in num_cols:
                        Q1 = df_lab[col].quantile(0.25)
                        Q3 = df_lab[col].quantile(0.75)
                        IQR = Q3 - Q1
                        df_lab = df_lab[(df_lab[col] >= (Q1 - 1.5 * IQR)) & (df_lab[col] <= (Q3 + 1.5 * IQR))]
                    st.session_state["datasets"][selected_table] = df_lab
                    st.success(f"Cleaned! Removed {initial_rows - len(df_lab)} outlier rows.")
                    st.rerun()
                else:
                    st.warning("No numeric columns found for outlier removal.")
    else:
        st.info("Upload data to access the Data Laboratory.")

with tab_query:
    st.markdown("### 💬 Natural Language SQL Query Engine")
    
    col_input, col_output = st.columns([1, 2])
    
    with col_input:
        # State-bound text area
        if "query_input" not in st.session_state:
            st.session_state["query_input"] = ""
            
        question = st.text_area("Ask a question about your data:", 
                               height=120, 
                               value=st.session_state["query_input"],
                               placeholder="e.g., 'Compare return rates for products over $100 against our top sellers.'")
        
        # Suggested Queries 
        st.markdown("⭐ **Suggested Insights**")
        example_queries = [
            "What is our total revenue growth performance?",
            "Identify top 5 performing channels by efficiency.",
            "Compare ROI across all available marketing datasets."
        ]
        
        for eq in example_queries:
            if st.button(eq, key=f"btn_{eq}", use_container_width=True):
                st.session_state["query_input"] = eq
                st.rerun()
        
        if st.button("🚀 Run Analytical Engine", type="primary", use_container_width=True):
            with st.spinner("🤖 AI is analyzing your request..."):
                try:
                    resp = agent.run(question)
                    resp_text = resp.content if hasattr(resp, "content") else str(resp)
                    sql = extract_sql_from_text(resp_text)
                    
                    if sql:
                        with st.expander("📝 Generated SQL Query", expanded=False):
                            st.code(sql, language="sql")
                        
                        res_df = run_sql(sql)
                        st.session_state["last_result"] = res_df
                        st.session_state["query_history"].append({
                            "question": question,
                            "sql": sql,
                            "timestamp": datetime.now(),
                            "rows": len(res_df)
                        })
                        
                        st.success(f"✅ Query executed successfully - {len(res_df):,} rows returned")
                        
                        with col_output:
                            st.dataframe(res_df, use_container_width=True, height=400)
                    else:
                        st.markdown(resp_text)
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Tip: Check that column names match your data schema")
    
    # Query history
    if st.session_state.get("query_history"):
        with st.expander("📜 Query History"):
            for idx, query in enumerate(reversed(st.session_state["query_history"][-5:])):
                st.caption(f"**{query['timestamp'].strftime('%H:%M:%S')}** - {query['question'][:50]}... ({query['rows']} rows)")

with tab_viz:
    st.markdown("### 📈 Advanced Interactive Visualizations")
    
    if st.session_state.get("last_result") is not None and not st.session_state["last_result"].empty:
        df_viz = st.session_state["last_result"]
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            chart_type = st.selectbox("Chart Type", ["auto", "line", "bar", "scatter"], 
                                     help="Select visualization type")
        
        with col1:
            fig = create_advanced_chart(df_viz, chart_type)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.dataframe(df_viz, use_container_width=True)
                
        # Download options
        st.download_button(
            label="📥 Download Data (CSV)",
            data=df_viz.to_csv(index=False).encode('utf-8'),
            file_name=f"proinsight_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("💡 Run a query in the 'Deep Query' tab first to visualize results")

with tab_forecast:
    st.markdown("### 🔮 AI-Powered Forecasting Engine")
    
    if st.session_state.get("last_result") is not None and not st.session_state["last_result"].empty:
        df_fore = st.session_state["last_result"]
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            days = st.slider("Forecast Period (days)", 7, 365, 30)
            confidence = st.checkbox("Show Confidence Intervals", value=True)
        
        with col1:
            if st.button("🎯 Generate Forecast", type="primary"):
                with st.spinner("🤖 Training forecasting model..."):
                    combined, msg = run_forecast(df_fore, periods=days)
                    
                    if combined is not None:
                        st.success(msg)
                        
                        # Create enhanced forecast chart
                        fig = go.Figure()
                        
                        # Actual data
                        actual_data = combined[combined['type'] == 'Actual']
                        fig.add_trace(go.Scatter(
                            x=actual_data[actual_data.columns[0]],
                            y=actual_data[actual_data.columns[1]],
                            name='Actual',
                            line=dict(color='#4F8BF9', width=3),
                            mode='lines'
                        ))
                        
                        # Forecast data
                        forecast_data = combined[combined['type'] == 'Forecast']
                        fig.add_trace(go.Scatter(
                            x=forecast_data[forecast_data.columns[0]],
                            y=forecast_data[forecast_data.columns[1]],
                            name='Forecast',
                            line=dict(color='#7B68EE', width=3, dash='dash'),
                            mode='lines'
                        ))
                        
                        # Confidence intervals
                        if confidence and 'lower_bound' in forecast_data.columns:
                            fig.add_trace(go.Scatter(
                                x=forecast_data[forecast_data.columns[0]],
                                y=forecast_data['upper_bound'],
                                fill=None,
                                mode='lines',
                                line=dict(color='rgba(123, 104, 238, 0.2)'),
                                showlegend=False
                            ))
                            fig.add_trace(go.Scatter(
                                x=forecast_data[forecast_data.columns[0]],
                                y=forecast_data['lower_bound'],
                                fill='tonexty',
                                mode='lines',
                                line=dict(color='rgba(123, 104, 238, 0.2)'),
                                name='95% Confidence'
                            ))
                        
                        fig.update_layout(
                            title="Forecast Analysis with Trend Projection",
                            template="plotly_dark",
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(family="Inter", size=12, color="#fafafa"),
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error(msg)
    else:
        st.warning("⚠️ Please run a time-series query first (must include date and numeric columns)")

with tab_report:
    st.markdown("### 📑 Executive Report Generator")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        client_name = st.text_input("Client Name", "Acme Corp", 
                                    help="Enter the client name for the report")
    
    with col2:
        report_type = st.selectbox("Report Type", ["Executive Summary", "Detailed Analysis", "Quick Brief"])
    
    if st.button("✨ Generate Premium Report", type="primary", use_container_width=True):
        with st.spinner("🤖 AI is analyzing data and generating insights..."):
            try:
                # Calculate comprehensive metrics
                metrics = calculate_advanced_metrics(st.session_state["datasets"])
                
                # Generate AI insights
                prompt = f"""You are writing a premium business intelligence report for {client_name}.
                
                Here are the calculated metrics from their data:
                {metrics}
                
                Write 3 distinct sections separated by '|||':
                
                1. EXECUTIVE SUMMARY (2-3 sentences): High-level overview of business performance
                
                2. STRATEGIC INSIGHTS (3-4 bullet points): Deep analysis of what the numbers reveal about business health, trends, and opportunities
                
                3. ACTION RECOMMENDATIONS (3 specific items): Concrete, actionable steps the client should take based on this data
                
                Be professional, data-driven, and specific. Use actual numbers from the metrics."""
                
                resp = agent.run(prompt)
                full_text = resp.content if hasattr(resp, "content") else str(resp)
                
                # Parse response
                parts = full_text.split("|||")
                summary = parts[0].strip() if len(parts) > 0 else "Analysis complete."
                insights = parts[1].strip() if len(parts) > 1 else "See metrics for details."
                recs = parts[2].strip() if len(parts) > 2 else "Continue monitoring performance."
                
                # Create report data
                report_data = {
                    "kpis": metrics,
                    "summary": summary,
                    "insights": insights,
                    "recommendations": recs
                }
                
                # Generate PDF
                pdf_bytes = create_executive_pdf(client_name, report_data)
                
                st.success("✅ Premium Report Generated Successfully!")
                
                # Preview
                st.markdown("### 📄 Professional Briefing Preview")
                col_preview1, col_preview2 = st.columns([1, 2])
                
                with col_preview1:
                    st.markdown("#### 💎 Performance Metrics")
                    for key, value in list(metrics.items())[:6]:
                        lab = key.replace('_', ' ').title()
                        val = format_metric_value(key, value)
                        st.markdown(f"""
                        <div class="metric-card" style="margin-bottom: 10px;">
                            <div class="metric-label">{lab}</div>
                            <div class="metric-value" style="font-size: 1.5rem;">{val}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col_preview2:
                    st.markdown("#### ⚡ Executive Briefing")
                    st.markdown(f"""
                    <div class="insight-box">
                        <strong>PROINSIGHT SUMMARY</strong><br>
                        {summary}
                    </div>
                    <div class="insight-box" style="border-left-color: var(--accent);">
                        <strong>STRATEGIC INTELLIGENCE</strong><br>
                        {insights}
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Download button
                st.download_button(
                    label="📥 Download Premium PDF Report",
                    data=pdf_bytes,
                    file_name=f"{client_name.replace(' ', '_')}_Executive_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"❌ Report Generation Error: {str(e)}")
                st.info("💡 Ensure you have uploaded data and the AI can access your metrics")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #8b92a7; font-size: 0.9rem;'>
    <strong>ProInsight Agency Platform</strong> v2.0 | Powered by Agno AI + OpenAI GPT-4o + DuckDB<br>
    Advanced Analytics • Predictive Forecasting • Executive Reporting
</div>
""", unsafe_allow_html=True)
