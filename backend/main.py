from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd
import duckdb
import os
import io
import re
from datetime import datetime
from functools import lru_cache

# Agno Imports
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckdb import DuckDbTools
from agno.tools.duckduckgo import DuckDuckGo

app = FastAPI(title="ProInsight SaaS Backend", version="3.2")

# ---------- Database & Scaling ----------
DB_PATH = "analytics.db"

def get_con():
    """Returns a connection to DuckDB or MotherDuck."""
    if os.getenv("MOTHERDUCK_TOKEN"):
        return duckdb.connect(f"md:?motherduck_token={os.getenv('MOTHERDUCK_TOKEN')}")
    return duckdb.connect(DB_PATH)

# ---------- SaaS Models ----------
class QueryRequest(BaseModel):
    query: str
    api_key: str
    session_id: Optional[str] = "default"

class QueryResponse(BaseModel):
    answer: str
    sql: Optional[str] = None
    market_context: Optional[List[str]] = None
    thought_process: Optional[List[str]] = None

# ---------- Caching (Ralph Superpower) ----------
@lru_cache(maxsize=128)
def get_cached_response(query_hash: str):
    """Simple LRU cache for high-frequency queries."""
    return None

# ---------- Agno Agent Team (Structured via GSD/Ralph Patterns) ----------

def get_supervisor_team(api_key: str):
    con = get_con()
    
    # 1. The Expert Data Analyst (SQL Engine)
    data_analyst = Agent(
        name="Analyst",
        role="Extracts precise business metrics using DuckDB SQL.",
        model=OpenAIChat(id="gpt-4o", api_key=api_key),
        tools=[DuckDbTools(connection=con)],
        instructions=[
            "Identify the correct tables from the database.",
            "Write optimized SQL for DuckDB.",
            "Always explain the 'Why' behind the numbers.",
            "Wrap SQL in ```sql blocks."
        ],
        show_tool_calls=True
    )

    # 2. The Market Researcher (Web Intelligence)
    market_researcher = Agent(
        name="Researcher",
        role="Provides external market context and competitive benchmarks.",
        model=OpenAIChat(id="gpt-4o", api_key=api_key),
        tools=[DuckDuckGo()],
        instructions=[
            "Find recent market trends related to the business query.",
            "Provide 2-3 specific external facts or benchmarks.",
            "Focus on high-value business impact."
        ],
        show_tool_calls=True
    )

    # 3. The ProInsight Supervisor (Executive Synthesis)
    # Porting Ralph/GSD 'Executive Governance' pattern
    supervisor = Agent(
        name="ProInsight Supervisor",
        team=[data_analyst, market_researcher],
        model=OpenAIChat(id="gpt-4o", api_key=api_key),
        instructions=[
            "You are the Lead Project Supervisor for ProInsight.",
            "PHASE 1: Direct the Analyst to pull hard internal data from DuckDB.",
            "PHASE 2: Direct the Researcher to find external context via the web.",
            "PHASE 3: Synthesize both into a 'Premium Executive Briefing'.",
            "Maintain a professional, strategic consulting tone.",
            "Ensure all recommendations are high-growth oriented."
        ],
        show_tool_calls=True,
        markdown=True
    )
    
    return supervisor

# ---------- Endpoints ----------

@app.post("/v1/data/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Ingests data into the SaaS persistent engine."""
    try:
        name = file.filename.replace(".csv", "").lower()
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        con = get_con()
        con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM df")
        return {"status": "success", "table": name, "rows": len(df)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/agent/analyze", response_model=QueryResponse)
async def analyze_query(request: QueryRequest):
    """Main SaaS endpoint for AI-powered analytics."""
    if not request.api_key:
        raise HTTPException(status_code=400, detail="OpenAI API Key is missing.")

    try:
        supervisor = get_supervisor_team(request.api_key)
        response = supervisor.run(request.query)
        
        # Extract SQL for the frontend visualization
        sql_match = re.search(r"```sql\s*(.*?)\s*```", response.content, re.DOTALL)
        sql = sql_match.group(1).strip() if sql_match else None
        
        return QueryResponse(
            answer=response.content,
            sql=sql,
            thought_process=["Coordinating Analyst...", "Running SQL...", "Fetching Web Context...", "Synthesizing Briefing..."]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
