# ai_data_analyst.py – Improved AI Data Analyst (Streamlit + DuckDB + Agno/OpenAI)

import os
import re
import time
import tempfile
import hashlib
import csv
from typing import Optional, List, Tuple
from pathlib import Path

import streamlit as st
import pandas as pd
import duckdb
import altair as alt

# Agno imports
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckdb import DuckDbTools
from agno.tools.pandas import PandasTools

# ---------- Config ----------
DEFAULT_LIMIT = 20000
ALLOWED_SQL_PREFIXES = (
    "SELECT", "WITH", "EXPLAIN", "SHOW", "DESCRIBE", "SUMMARIZE", "CREATE OR REPLACE TABLE"
)
CACHE_MAX_ITEMS = 200
MAX_FILE_SIZE_MB = 100
TABLE_NAME = "uploaded_data"

# ---------- Utilities ----------
def slug(s: str) -> str:
    """Generate a short hash slug from a string."""
    return hashlib.sha256(s.encode()).hexdigest()[:12]

def ensure_state():
    """Initialize session state variables."""
    keys = {
        "duckdb_con": None,
        "uploaded_df": None,
        "uploaded_temp_path": None,
        "openai_key": None,
        "agent": None,
        "last_agent_response": None,
        "last_sql": "",
        "last_result_df": None,
        "query_history": [],
        "result_cache": {},
        "file_info": None,
    }
    for k, v in keys.items():
        if k not in st.session_state:
            st.session_state[k] = v

def get_duckdb_con() -> duckdb.DuckDBPyConnection:
    """Get or create DuckDB connection."""
    if st.session_state.get("duckdb_con") is None:
        st.session_state["duckdb_con"] = duckdb.connect(database=":memory:")
    return st.session_state["duckdb_con"]

def is_safe_sql(sql: str) -> bool:
    """Validate SQL is safe to execute."""
    if not sql or not isinstance(sql, str):
        return False
    s = sql.strip().upper()
    return any(s.startswith(p) for p in ALLOWED_SQL_PREFIXES)

def inject_limit(sql: str, limit: int = DEFAULT_LIMIT) -> str:
    """Add LIMIT clause to SELECT queries."""
    s = sql.strip()
    if s.upper().startswith("SELECT") and "LIMIT" not in s.upper():
        return f"SELECT * FROM ({s.rstrip(';')}) LIMIT {limit}"
    return s

def cache_get(key: str):
    """Retrieve cached query result."""
    return st.session_state["result_cache"].get(key)

def cache_set(key: str, value):
    """Store query result in cache with LRU eviction."""
    cache = st.session_state["result_cache"]
    if len(cache) >= CACHE_MAX_ITEMS:
        oldest = next(iter(cache))
        cache.pop(oldest, None)
    cache[key] = value

# ---------- SQL execution helper ----------
def run_sql_return_df(
    sql: str,
    uploaded_df: Optional[pd.DataFrame] = None,
    table_name: str = TABLE_NAME
) -> pd.DataFrame:
    """Execute SQL query and return results as DataFrame."""
    if not is_safe_sql(sql):
        raise ValueError(
            "SQL blocked by safety rules. Only SELECT/WITH/EXPLAIN/SHOW/DESCRIBE/SUMMARIZE allowed."
        )

    con = get_duckdb_con()

    # Register uploaded_df into DuckDB
    if uploaded_df is not None and isinstance(uploaded_df, pd.DataFrame) and not uploaded_df.empty:
        try:
            con.register(table_name, uploaded_df)
        except Exception as e:
            # Fallback: write to parquet then read
            try:
                with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
                    uploaded_df.to_parquet(tmp.name, index=False)
                    con.execute(
                        f"CREATE OR REPLACE TABLE {table_name} AS "
                        f"SELECT * FROM read_parquet('{tmp.name}')"
                    )
                    os.remove(tmp.name)
            except Exception as fallback_e:
                raise RuntimeError(f"Failed to register data: {e}, fallback error: {fallback_e}")

    sql_exec = inject_limit(sql, DEFAULT_LIMIT)
    try:
        df = con.execute(sql_exec).df()
        return df
    except Exception as e:
        raise RuntimeError(f"DuckDB execution error: {e}") from e

# ---------- Extract SQL from agent text ----------
def extract_sql_from_text(text: str) -> str:
    """Extract SQL query from agent response text."""
    if not text:
        return ""

    # Try code block first
    blocks = re.findall(r"```(?:sql)?\s*([\s\S]*?)```", text, flags=re.IGNORECASE)
    if blocks:
        return blocks[0].strip()

    # Try to find SQL statement
    m = re.search(
        r"((?:SELECT|WITH|EXPLAIN|CREATE|SHOW|DESCRIBE|SUMMARIZE)[\s\S]{10,3000})",
        text,
        flags=re.IGNORECASE
    )
    if m:
        candidate = m.group(1).strip()
        lines = candidate.splitlines()
        cleaned = []
        for ln in lines:
            if re.match(r"^\s*(NOTE:|CHART:|Explanation:|#)", ln, flags=re.IGNORECASE):
                break
            cleaned.append(ln)
        return "\n".join(cleaned).strip()

    return ""

# ---------- Display helpers ----------
def show_downloads(df: pd.DataFrame, prefix: str = "results"):
    """Show download buttons for CSV and XLSX."""
    if df is None or df.empty:
        return

    st.download_button(
        "📥 Download CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name=f"{prefix}.csv",
        mime="text/csv"
    )

    try:
        import io
        out = io.BytesIO()
        df.to_excel(out, index=False, engine="openpyxl")
        out.seek(0)
        st.download_button(
            "📥 Download XLSX",
            out.getvalue(),
            file_name=f"{prefix}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.warning(f"Could not generate XLSX: {e}")

def auto_chart(df: pd.DataFrame):
    """Auto-generate chart from results."""
    if df is None or df.empty:
        st.info("No rows to chart.")
        return

    # Find date column
    date_col = None
    for c in df.columns:
        if "date" in c.lower():
            date_col = c
            break

    # Find numeric column
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    numeric_col = None

    if any(c.lower() == "revenue" for c in df.columns):
        numeric_col = next(c for c in df.columns if c.lower() == "revenue")
    elif numeric_cols:
        numeric_col = numeric_cols[0]

    # Time series chart
    if date_col and numeric_col:
        try:
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors="coerce")
            chart_df = df_temp.groupby(df_temp[date_col].dt.date)[numeric_col].sum().reset_index()
            chart_df[date_col] = pd.to_datetime(chart_df[date_col])

            chart = (
                alt.Chart(chart_df)
                .mark_bar()
                .encode(
                    x=alt.X(date_col, type="temporal", title="Date"),
                    y=alt.Y(numeric_col, type="quantitative", title=numeric_col),
                    tooltip=[date_col, numeric_col]
                )
                .properties(width=800, height=400)
            )
            st.altair_chart(chart, use_container_width=True)
            return
        except Exception as e:
            st.warning(f"Could not create time series chart: {e}")

    # Simple bar chart
    if numeric_col:
        if len(df) <= 500:
            try:
                chart = (
                    alt.Chart(df.reset_index())
                    .mark_bar()
                    .encode(
                        x=alt.X('index:O', title='Index'),
                        y=alt.Y(numeric_col, type="quantitative"),
                        tooltip=list(df.columns)
                    )
                    .properties(width=800, height=400)
                )
                st.altair_chart(chart, use_container_width=True)
            except Exception as e:
                st.warning(f"Chart rendering error: {e}")
        else:
            st.info("Result is large – consider grouping or filtering data.")
    else:
        st.info("No numeric column found for charting.")

# ---------- File read helper ----------
def preprocess_and_save(file) -> Tuple[Optional[str], Optional[List[str]], Optional[pd.DataFrame]]:
    """Read and preprocess uploaded file."""
    try:
        file_size_mb = file.size / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            st.error(f"File too large ({file_size_mb:.1f}MB). Max: {MAX_FILE_SIZE_MB}MB")
            return None, None, None

        if file.name.endswith(".csv"):
            df = pd.read_csv(file, low_memory=False)
        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file)
        else:
            st.error("Unsupported format. Use CSV or XLSX.")
            return None, None, None

        # Parse date columns
        for c in df.columns:
            if "date" in c.lower():
                try:
                    df[c] = pd.to_datetime(df[c], errors="coerce")
                except Exception:
                    pass

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='w') as tmp:
            df.to_csv(tmp.name, index=False, quoting=csv.QUOTE_MINIMAL)
            temp_path = tmp.name

        return temp_path, df.columns.tolist(), df

    except Exception as e:
        st.error(f"Failed to read file: {e}")
        return None, None, None

# ---------- UI / Main ----------
st.set_page_config(
    page_title="AI Data Analyst",
    layout="wide",
    initial_sidebar_state="expanded"
)
ensure_state()

st.title("🧠 AI Data Analyst – Advanced")
st.markdown("Upload data and ask natural language questions. AI generates and executes SQL.")

# ========== SIDEBAR ==========
with st.sidebar:
    st.header("⚙️ Settings & Configuration")

    # API Key
    st.subheader("OpenAI API Key")
    api = st.text_input("Paste your OpenAI API key", type="password", key="api_input")
    if api:
        st.session_state["openai_key"] = api
        st.success("API key set (this session)")

    if st.button("📤 Load from environment (OPENAI_API_KEY)"):
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key:
            st.session_state["openai_key"] = env_key
            st.success("Loaded from OPENAI_API_KEY env var.")
        else:
            st.warning("No OPENAI_API_KEY found in environment.")

    st.divider()

    # Model selection
    st.subheader("Model Settings")
    model_choice = st.selectbox(
        "Select model",
        ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        index=1
    )
    temp = st.slider("Temperature", 0.0, 1.0, 0.1, 0.05)

    st.divider()

    # Session info
    st.subheader("Session Info")
    uploaded_rows = 0 if st.session_state['uploaded_df'] is None else len(st.session_state['uploaded_df'])
    uploaded_cols = 0 if st.session_state['uploaded_df'] is None else len(st.session_state['uploaded_df'].columns)
    st.metric("Uploaded Rows", uploaded_rows)
    st.metric("Columns", uploaded_cols)
    st.metric("Cached Queries", len(st.session_state['result_cache']))

    st.divider()

    # Session controls
    col_clear, col_reset = st.columns(2)
    with col_clear:
        if st.button("🗑️ Clear Cache"):
            st.session_state["result_cache"] = {}
            st.success("Cache cleared.")

    with col_reset:
        if st.button("🔄 Reset Session"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

# ========== MAIN CONTENT ==========

# Upload section
st.header("📤 Upload Data")
col_upload, col_info = st.columns([3, 1])

with col_upload:
    uploaded_file = st.file_uploader("Choose CSV or XLSX file", type=["csv", "xlsx"])

with col_info:
    st.write("📋 Supported formats")
    st.caption("• CSV\n• XLSX")

if uploaded_file is not None:
    temp_path, cols, df = preprocess_and_save(uploaded_file)
    if temp_path and df is not None:
        st.session_state["uploaded_df"] = df
        st.session_state["uploaded_temp_path"] = temp_path
        st.session_state["file_info"] = {
            "name": uploaded_file.name,
            "size": uploaded_file.size,
            "rows": len(df),
            "columns": len(df.columns)
        }
        st.success(
            f"✅ Uploaded **{uploaded_file.name}** – "
            f"{len(df):,} rows, {len(df.columns)} columns"
        )
        with st.expander("📊 Preview Data"):
            st.dataframe(df.head(50), use_container_width=True)
        st.write("**Columns:**", ", ".join(df.columns.tolist()))

# Check API key
if not st.session_state.get("openai_key"):
    st.warning("⚠️ OpenAI API key required. Set in the sidebar.")
    st.stop()

# Initialize agent
if st.session_state.get("agent") is None:
    try:
        st.session_state["agent"] = Agent(
            model=OpenAIChat(id=model_choice, api_key=st.session_state["openai_key"]),
            tools=[DuckDbTools(), PandasTools()],
            system_message=(
                f"You are a helpful data analyst assistant. "
                f"The user has uploaded a table called '{TABLE_NAME}'. "
                f"When asked to analyze data, write SQL queries using DuckDB syntax. "
                f"Always output SQL in a ```sql``` code block. "
                f"Be concise and helpful."
            ),
            markdown=True,
        )
    except Exception as e:
        st.error(f"❌ Failed to initialize agent: {e}")
        st.stop()

agent = st.session_state["agent"]

# Question section
st.header("🔍 Ask Your Question")
question = st.text_area(
    "What would you like to know about your data?",
    height=120,
    placeholder="e.g., 'Show total revenue by month' or 'Find top 10 customers by sales'"
)

# Action buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🤖 Generate SQL", use_container_width=True):
        if not question.strip():
            st.warning("Please enter a question.")
        elif st.session_state.get('uploaded_df') is None:
            st.warning("Please upload data first.")
        else:
            with st.spinner("Generating SQL..."):
                try:
                    resp = agent.run(question)
                    response_text = resp.content if hasattr(resp, "content") else str(resp)
                    st.session_state["last_agent_response"] = response_text
                    st.success("✅ SQL generated. Check below.")
                except Exception as e:
                    st.error(f"Agent error: {e}")

with col2:
    if st.button("⚡ Auto-Run (Generate + Execute)", use_container_width=True):
        if not question.strip():
            st.warning("Please enter a question.")
        elif st.session_state.get('uploaded_df') is None:
            st.warning("Please upload data first.")
        else:
            with st.spinner("Running..."):
                try:
                    resp = agent.run(question)
                    response_text = resp.content if hasattr(resp, "content") else str(resp)
                    st.session_state["last_agent_response"] = response_text

                    sql = extract_sql_from_text(response_text)
                    if not sql:
                        st.warning("No SQL found. Use 'Force SQL' below.")
                    else:
                        st.session_state["last_sql"] = sql
                        cache_key = hashlib.sha256(
                            (TABLE_NAME + sql).encode()
                        ).hexdigest()

                        cached = cache_get(cache_key)
                        if cached is not None:
                            st.info("📦 Using cached result.")
                            df_out = cached
                        else:
                            df_out = run_sql_return_df(
                                sql,
                                uploaded_df=st.session_state["uploaded_df"]
                            )
                            cache_set(cache_key, df_out)

                        st.session_state["last_result_df"] = df_out
                        st.session_state["query_history"].insert(
                            0,
                            {
                                "question": question,
                                "sql": sql,
                                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                                "rows": len(df_out)
                            }
                        )
                        st.success(f"✅ Executed. {len(df_out)} rows returned.")
                except Exception as e:
                    st.error(f"Execution error: {e}")

with col3:
    if st.button("📖 Show Response", use_container_width=True):
        if st.session_state.get("last_agent_response"):
            st.info("Agent Response:")
            st.markdown(st.session_state["last_agent_response"])
        else:
            st.info("Generate SQL first.")

st.divider()

# Force SQL generation
if st.button("🔨 Force Strict SQL", help="Request SQL-only response from agent"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Generating SQL (strict mode)..."):
            try:
                strict_prompt = (
                    question + "\n\n"
                    "IMPORTANT: Return ONLY a SQL query inside ```sql``` code block. "
                    f"Use table '{TABLE_NAME}'. Use DuckDB syntax. No explanation."
                )
                resp = agent.run(strict_prompt)
                response_text = resp.content if hasattr(resp, "content") else str(resp)
                st.session_state["last_agent_response"] = response_text
                st.success("✅ SQL generated (strict).")
            except Exception as e:
                st.error(f"Error: {e}")

# SQL Editor & Execution
extracted = (
    extract_sql_from_text(st.session_state.get("last_agent_response", ""))
    or st.session_state.get("last_sql", "")
)

if extracted:
    st.markdown("### ✏️ SQL Editor")
    edited = st.text_area(
        "Edit SQL before executing",
        value=extracted,
        height=220,
        key=f"sql_{slug(extracted)}"
    )

    ex_col1, ex_col2, ex_col3 = st.columns(3)

    with ex_col1:
        if st.button("▶️ Execute", use_container_width=True):
            if not is_safe_sql(edited):
                st.error("❌ SQL blocked by safety rules.")
            else:
                with st.spinner("Executing..."):
                    try:
                        cache_key = hashlib.sha256(
                            (TABLE_NAME + edited).encode()
                        ).hexdigest()
                        cached = cache_get(cache_key)
                        if cached is not None:
                            st.info("📦 Using cached result.")
                            df_out = cached
                        else:
                            df_out = run_sql_return_df(
                                edited,
                                uploaded_df=st.session_state["uploaded_df"]
                            )
                            cache_set(cache_key, df_out)

                        st.session_state["last_result_df"] = df_out
                        st.session_state["query_history"].insert(
                            0,
                            {
                                "question": question or "<manual>",
                                "sql": edited,
                                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                                "rows": len(df_out)
                            }
                        )
                        st.success(f"✅ Executed. {len(df_out):,} rows.")
                    except Exception as e:
                        st.error(f"❌ Execution failed: {e}")

    with ex_col2:
        if st.button("💾 Save to History", use_container_width=True):
            st.session_state["query_history"].insert(
                0,
                {
                    "question": question or "<manual>",
                    "sql": edited,
                    "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "rows": 0
                }
            )
            st.success("Saved to history.")

    with ex_col3:
        if st.button("🗑️ Clear Result", use_container_width=True):
            st.session_state["last_result_df"] = None
            st.success("Cleared.")

# Display results
if st.session_state.get("last_result_df") is not None:
    st.header("📊 Results")
    df_show = st.session_state["last_result_df"]

    col_table, col_stats = st.columns([3, 1])
    with col_table:
        st.dataframe(df_show, use_container_width=True)
    with col_stats:
        st.metric("Rows", len(df_show))
        st.metric("Columns", len(df_show.columns))

    show_downloads(df_show, prefix="results")

    with st.expander("📈 Auto Chart"):
        auto_chart(df_show)

# Sidebar: Query history
st.sidebar.markdown("---")
st.sidebar.subheader("📜 Query History")

if st.session_state["query_history"]:
    for i, h in enumerate(st.session_state["query_history"][:30]):
        with st.sidebar.expander(
            f"{i+1}. {h['time']} ({h.get('rows', '?')} rows)"
        ):
            st.write("**Q:**", h["question"])
            st.code(h["sql"], language="sql")
            if st.button(f"Re-run", key=f"rerun_{i}"):
                try:
                    with st.spinner("Running..."):
                        df_r = run_sql_return_df(
                            h["sql"],
                            uploaded_df=st.session_state["uploaded_df"]
                        )
                        st.session_state["last_result_df"] = df_r
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
else:
    st.sidebar.info("No queries yet.")

st.sidebar.divider()
st.sidebar.caption(
    "💡 **Tip:** If agent doesn't return SQL, click 'Force Strict SQL'. "
    "Edit SQL in the editor before executing."
)

# Footer
st.divider()
st.caption(
    "🔐 Data is processed locally in DuckDB. "
    "Only your question is sent to OpenAI."
)