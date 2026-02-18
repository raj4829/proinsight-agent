from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd
import duckdb
import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckdb import DuckDbTools
from agno.tools.duckduckgo import DuckDuckGo
import re
from functools import lru_cache

app = FastAPI(title="ProInsight SaaS Backend", version="3.1")

# ---------- Persistence & Data ----------
DB_PATH = "analytics.db"

def get_duckdb_con():
    # MotherDuck integration if token provided
    if os.getenv("MOTHERDUCK_TOKEN"):
        return duckdb.connect(f"md:?motherduck_token={os.getenv('MOTHERDUCK_TOKEN')}")
    return duckdb.connect(DB_PATH)

# ---------- Models ----------
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"
    api_key: str

class QueryResponse(BaseModel):
    answer: str
    sql: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None

# ---------- Caching ----------
@lru_cache(maxsize=128)
def get_cached_insight(query: str, session_id: str):
    # This is a placeholder for actual response caching
    return None

# ---------- Agents ----------
def get_agent_team(api_key: str):
    con = get_duckdb_con()
    
    # 1. Data Analyst (SQL Expert)
    data_analyst = Agent(
        name="DataAnalyst",
        role="Runs optimized SQL queries on DuckDB to extract business insights.",
        model=OpenAIChat(id="gpt-4o", api_key=api_key),
        tools=[DuckDbTools(connection=con)],
        instructions=[
            "Use standard DuckDB SQL.",
            "Always wrap SQL in ```sql blocks.",
            "If column names have spaces, use double quotes.",
        ],
        show_tool_calls=True,
    )

    # 2. Web Researcher (Context Expert)
    web_researcher = Agent(
        name="WebResearcher",
        role="Searches the web for market trends and external context.",
        model=OpenAIChat(id="gpt-4o", api_key=api_key),
        tools=[DuckDuckGo()],
        instructions=["Provide 2-3 high-value external market insights related to the query."],
        show_tool_calls=True,
    )

    # 3. Supervisor (The Orchestrator)
    supervisor = Agent(
        name="Supervisor",
        team=[data_analyst, web_researcher],
        model=OpenAIChat(id="gpt-4o", api_key=api_key),
        instructions=[
            "You are the ProInsight Supervisor.",
            "First, ask the DataAnalyst to run SQL to get hard numbers.",
            "Second, ask the WebResearcher for external market context.",
            "Finally, synthesize the data and context into a professional executive briefing.",
        ],
        show_tool_calls=True,
        markdown=True,
    )
    
    return supervisor

# ---------- Endpoints ----------
@app.post("/v1/agent/analyze", response_model=QueryResponse)
async def analyze(request: QueryRequest):
    if not request.api_key:
        raise HTTPException(status_code=400, detail="OpenAI API Key is required.")

    # Check cache
    cached = get_cached_insight(request.query, request.session_id)
    if cached:
        return cached

    try:
        agent = get_agent_team(request.api_key)
        response = agent.run(request.query)
        
        # Extract SQL if present in the conversation
        sql_match = re.search(r"```sql\s*(.*?)\s*```", response.content, re.DOTALL)
        sql = sql_match.group(1) if sql_match else None
        
        return QueryResponse(
            answer=response.content,
            sql=sql,
            tool_calls=[] # For now returning empty as Agno handles printing tool calls internally
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
