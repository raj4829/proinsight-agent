# Architecture Overview

## System Flow
1. **Ingestion**: User uploads CSV/XLSX files via Streamlit sidebar.
2. **Registration**: Files are loaded into Pandas DataFrames and registered as tables in a `:memory:` DuckDB instance.
3. **Reasoning**: The Agno Agent (GPT-4o) converts natural language questions into optimized DuckDB SQL based on the detected schema.
4. **Execution**: SQL is run against DuckDB, returning results as DataFrames.
5. **Visualization**: Results are passed to Plotly for interactive charts.
6. **Persistence**: (Disabled in current elite version) Reverted from modular to single-file for portability.

## Directory Structure
- `/`: Main application logic (`pro_insight_analyst.py`) and config (`requirements.txt`).
- `.agent/`: GSD workflow and automation definitions.
- `.planning/`: Project context and roadmap (GSD state).
- `design-system/`: Design governance and master rules.
- `portfolio/`: Presentation assets and sales documentation.
