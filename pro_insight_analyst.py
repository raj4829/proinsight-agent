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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    .stApp { 
        background: linear-gradient(135deg, #0E1117 0%, #1a1d29 100%);
        color: #FAFAFA; 
        font-family: 'Inter', sans-serif; 
    }
    .stSidebar { 
        background: linear-gradient(180deg, #1e2130 0%, #262730 100%);
        border-right: 1px solid #2d3142;
    }
    h1 { 
        background: linear-gradient(90deg, #4F8BF9 0%, #7B68EE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.5rem;
    }
    h2, h3 { 
        color: #4F8BF9; 
        font-weight: 600;
    }
    .stButton>button { 
        background: linear-gradient(90deg, #4F8BF9 0%, #7B68EE 100%);
        color: white; 
        border-radius: 12px; 
        font-weight: 600;
        border: none;
        padding: 0.75rem 2rem;
        box-shadow: 0 4px 15px rgba(79, 139, 249, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(79, 139, 249, 0.4);
    }
    .stTextInput>div>div>input { 
        border-radius: 10px;
        border: 1px solid #3d4152;
        background: #1e2130;
        color: #fafafa;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e2130 0%, #262730 100%);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid #3d4152;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4F8BF9 0%, #7B68EE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #8b92a7;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .insight-box {
        background: linear-gradient(135deg, #2d3142 0%, #3d4152 100%);
        border-left: 4px solid #4F8BF9;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    /* Mobile Responsiveness */
    @media (max-width: 600px) {
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.4rem !important; }
        .metric-value { font-size: 1.8rem !important; }
        .stButton>button { width: 100%; }
        .block-container { padding-left: 1rem; padding-right: 1rem; }
        /* Ensure columns stack on mobile */
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

# Initialize Agent
if st.session_state.get("agent") is None or st.session_state["datasets"]:
    schema_desc = "Available Tables:\n"
    for name, df in st.session_state["datasets"].items():
        cols_formatted = []
        for col in df.columns:
            if ' ' in col:
                cols_formatted.append(f'"{col}"')
            else:
                cols_formatted.append(col)
        schema_desc += f"- Table '{name}': Columns [{', '.join(cols_formatted)}]\n"
    
    st.session_state["agent"] = Agent(
        model=OpenAIChat(id="gpt-4o", api_key=st.session_state["openai_key"]),
        description="You are an elite Data Architect and Business Intelligence expert specializing in DuckDB.",
        instructions=[
            f"{schema_desc}",
            "Write optimized DuckDB SQL queries with proper indexing and aggregation.",
            "CRITICAL: Column names with spaces MUST be wrapped in double quotes (e.g., \"Units Sold\").",
            "Use descriptive table aliases (e.g., ssd for sample_sales_data).",
            "Include comments in SQL for complex queries.",
            "Always wrap SQL in ```sql``` code blocks.",
            "Provide brief explanations of query logic when relevant."
        ],
        markdown=True
    )

agent = st.session_state["agent"]

# Header
st.markdown("# 🚀 ProInsight Agency Platform")
st.markdown("*Advanced AI-Powered Business Intelligence & Analytics*")
st.markdown("---")

# Tabs
tab_overview, tab_query, tab_viz, tab_forecast, tab_report = st.tabs([
    "📊 Overview", "💬 Deep Query", "📈 Interactive Viz", "🔮 Forecasting", "📑 Reports"
])

with tab_overview:
    st.markdown("### 📊 Business Intelligence Dashboard")
    
    if st.session_state["datasets"]:
        # Calculate advanced metrics
        metrics = calculate_advanced_metrics(st.session_state["datasets"])
        
        # Display key metrics in cards
        st.markdown("#### Key Performance Indicators")
        
        # Filter and display most important metrics
        priority_metrics = {k: v for k, v in metrics.items() 
                          if any(x in k for x in ['total_revenue', 'total_cost', 'roas', 'roi', 'growth'])}
        
        if priority_metrics:
            cols = st.columns(min(4, len(priority_metrics)))
            for idx, (key, value) in enumerate(list(priority_metrics.items())[:4]):
                with cols[idx]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">{key.replace('_', ' ').title()}</div>
                        <div class="metric-value">{format_metric_value(key, value)}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick insights
        st.markdown("#### 🎯 Quick Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="insight-box">
                <strong>📈 Data Coverage</strong><br>
                {} dataset(s) loaded with {:,} total records
            </div>
            """.format(len(st.session_state["datasets"]), 
                      sum(len(df) for df in st.session_state["datasets"].values())), 
            unsafe_allow_html=True)
        
        with col2:
            if 'calculated_roas' in metrics:
                roas_val = metrics['calculated_roas']
                roas_status = "Excellent" if roas_val > 3 else "Good" if roas_val > 2 else "Needs Improvement"
                st.markdown(f"""
                <div class="insight-box">
                    <strong>💰 ROAS Performance</strong><br>
                    {roas_val:.2f}x - {roas_status}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📁 Upload data files in the sidebar to see your dashboard")

with tab_query:
    st.markdown("### 💬 Natural Language SQL Query Engine")
    
    col_input, col_output = st.columns([1, 2])
    
    with col_input:
        question = st.text_area("Ask a question about your data:", 
                               height=150, 
                               placeholder="e.g., 'Show profit by product with ad spend analysis'")
        
        if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
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
                col_preview1, col_preview2 = st.columns(2)
                
                with col_preview1:
                    st.markdown("#### 📊 Key Metrics")
                    for key, value in list(metrics.items())[:6]:
                        st.metric(
                            label=key.replace('_', ' ').title(),
                            value=format_metric_value(key, value)
                        )
                
                with col_preview2:
                    st.markdown("#### 📝 Executive Summary Preview")
                    st.info(summary[:250] + "...")
                
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
