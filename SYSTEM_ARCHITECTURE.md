# 🏗️ ProInsight System Architecture: Data Flow & Agentic Pattern

## Executive Summary
This document serves as the **canonical reference** for understanding how ProInsight implements the **Agno Agentic Pattern** for SQL generation rather than direct Python execution. This architecture ensures safety, auditability, and leverages DuckDB's OLAP performance.

---

## 1. Core Data Flow Pipeline

```
┌─────────────────┐
│  CSV/Excel      │
│  Upload         │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  register_dataset()                 │
│  • Sanitizes table name             │
│  • Auto-detects date columns        │
│  • Registers DataFrame → DuckDB     │
│  • Stores in session_state          │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  DuckDB In-Memory Database          │
│  • OLAP-optimized                   │
│  • Multi-table support              │
│  • Persisted in st.session_state    │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Agno Agent (SQL Generator)         │
│  • Model: gpt-4o                    │
│  • Instructions: Schema + DuckDB    │
│  • Output: SQL wrapped in ```sql``` │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  extract_sql_from_text()            │
│  • Regex parser for code blocks     │
│  • Safety layer (no exec())         │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  run_sql()                          │
│  • Executes via DuckDB connector    │
│  • Returns pd.DataFrame             │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Streamlit Display Layer            │
│  • Tables (st.dataframe)            │
│  • Charts (Plotly)                  │
│  • Reports (FPDF)                   │
└─────────────────────────────────────┘
```

---

## 2. Agno Agent Configuration

### Current Implementation (Lines 266-271)
```python
st.session_state["agent"] = Agent(
    model=OpenAIChat(id="gpt-4o", api_key=st.session_state["openai_key"]),
    description="You are a Principal Data Architect.",
    instructions=[
        f"{schema_desc}",  # Dynamic schema injection
        "Write DuckDB SQL.",
        "Wrap SQL in ```sql``` blocks."
    ],
    markdown=True
)
```

### Key Design Decisions
1. **No Tools Attached**: The agent is intentionally "tool-less" to force SQL-only output.
2. **Dynamic Schema Injection**: The `schema_desc` variable is rebuilt on every dataset change, ensuring the agent always knows the current table structure.
3. **DuckDB Syntax Enforcement**: Instructions explicitly state "DuckDB SQL" to leverage dialect-specific features (e.g., `STRFTIME`, `QUALIFY`).

---

## 3. Why This Pattern? (Agno vs. Direct Execution)

### ❌ Anti-Pattern: Direct Python Execution
```python
# NEVER DO THIS
agent = Agent(tools=[PythonTools()])
resp = agent.run("Calculate total revenue")
# Agent writes: df['Revenue'].sum()
# Security risk: Arbitrary code execution
```

### ✅ ProInsight Pattern: SQL Generation
```python
# CURRENT APPROACH
resp = agent.run("Show total revenue by product")
sql = extract_sql_from_text(resp.content)
# Agent writes: SELECT Product, SUM(Revenue) FROM sales GROUP BY Product
# App executes: run_sql(sql) → Safe, auditable, fast
```

**Benefits**:
- **Security**: SQL is sandboxed; no file system access.
- **Performance**: DuckDB is 10-100x faster than Pandas for aggregations.
- **Auditability**: Every query is logged and visible to the user.

---

## 4. Multi-Table JOIN Architecture

### Schema Discovery (Lines 262-264)
```python
schema_desc = "Available Tables:\n"
for name, df in st.session_state["datasets"].items():
    schema_desc += f"- Table '{name}': Columns {list(df.columns)}\n"
```

### Example Agent Output
**User Query**: "Join sales and ad_spend on Date"

**Agent Generates**:
```sql
SELECT 
    s.Date,
    s.Revenue,
    a.Ad_Spend,
    (s.Revenue / a.Ad_Spend) AS ROAS
FROM sample_sales_data s
INNER JOIN sample_ad_spend a ON s.Date = a.Date
```

**Why This Works**:
- The agent receives the full schema upfront.
- DuckDB handles the join execution natively.
- No Pandas merge() overhead.

---

## 5. Session State Management

### Critical State Variables (Lines 28-34)
```python
keys = {
    "duckdb_con": None,      # Persistent DB connection
    "datasets": {},          # {table_name: DataFrame}
    "openai_key": None,      # API credential
    "agent": None,           # Agno Agent instance
    "last_result": None,     # Last query result (for viz/forecast)
}
```

### Why Session State?
Streamlit reruns the entire script on every interaction. Without `st.session_state`:
- DuckDB connection would reset → "Table not found" errors
- Agent would reinitialize → Wasted API calls
- Uploaded data would disappear → Poor UX

---

## 6. Advanced Features Leveraging This Architecture

### 6.1 Forecasting (Lines 112-142)
- **Input**: Last SQL query result (`st.session_state["last_result"]`)
- **Process**: Scikit-Learn trains on DuckDB-extracted data
- **Output**: Combined "Actual + Forecast" DataFrame → Plotly chart

### 6.2 PDF Reporting (Lines 323-350)
- **Metrics Calculation**: Direct DataFrame operations (`calculate_hard_metrics`)
- **AI Synthesis**: Agent interprets metrics → Strategic insights
- **PDF Generation**: FPDF renders structured report

---

## 7. DuckDB-Specific Optimizations

### Date Handling
```python
# Auto-conversion during upload (Lines 240-243)
for col in df.columns:
    if "date" in col.lower() or "time" in col.lower():
        try: df[col] = pd.to_datetime(df[col])
        except: pass
```

### Why This Matters
DuckDB's `DATE` type enables:
- `EXTRACT(YEAR FROM Date)` for time-series grouping
- `DATE_TRUNC('month', Date)` for aggregations
- Faster filtering than string comparisons

---

## 8. Future Enhancements (Agno-Native)

### 8.1 Add AgentKnowledge
```python
from agno.knowledge import AgentKnowledge

knowledge = AgentKnowledge(
    vector_db=...,
    documents=["DuckDB_Best_Practices.md", "SQL_Patterns.md"]
)

agent = Agent(
    model=OpenAIChat(...),
    knowledge=knowledge,  # RAG for complex queries
    instructions=[...]
)
```

### 8.2 Add Custom Tools (Safe)
```python
from agno.tools import Tool

def get_table_stats(table_name: str) -> dict:
    """Returns row count, column types, null percentages."""
    df = st.session_state["datasets"][table_name]
    return {
        "rows": len(df),
        "columns": df.dtypes.to_dict(),
        "nulls": df.isnull().sum().to_dict()
    }

agent = Agent(
    tools=[Tool(function=get_table_stats)],
    ...
)
```

---

## 9. Debugging Checklist

### Issue: "Table not found"
- ✅ Check `st.session_state["datasets"]` is populated
- ✅ Verify `register_dataset()` was called
- ✅ Ensure table name matches sanitized version (lowercase, no spaces)

### Issue: "Agent returns text instead of SQL"
- ✅ Check `extract_sql_from_text()` regex
- ✅ Verify agent instructions include "Wrap SQL in ```sql``` blocks"
- ✅ Test with explicit prompt: "Write SQL query for..."

### Issue: "SQL syntax error"
- ✅ Confirm DuckDB dialect (not PostgreSQL/MySQL)
- ✅ Check column names match schema exactly (case-sensitive)
- ✅ Use `run_sql()` error messages to debug

---

## 10. Terminology Clarification

| Term | Definition | Example |
|------|------------|---------|
| **Antigravity** | Google's AI-powered IDE (this environment) | The tool you're using now |
| **Agno** | Python framework for building AI agents | `from agno.agent import Agent` |
| **DuckDB** | In-memory OLAP database | `duckdb.connect(":memory:")` |
| **Streamlit** | Web UI framework | `st.dataframe(df)` |

**Critical**: When asking Antigravity for help, specify "using Agno framework" to get framework-specific code (not generic LangChain/CrewAI patterns).

---

## Conclusion

This architecture is **production-ready** because:
1. **Safe**: No arbitrary code execution
2. **Fast**: DuckDB OLAP performance
3. **Scalable**: Multi-table JOINs without memory overhead
4. **Maintainable**: Single-file design with clear separation of concerns

All future features should follow the **Agno Agentic Pattern**: Tools + Knowledge + Instructions → Structured Output → Safe Execution.
