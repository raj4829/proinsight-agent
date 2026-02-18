# 🔌 ProInsight AI Plugin Directory

This project is governed by a hybrid "AI Operating System" combining several high-performance meta-prompting frameworks. Always leverage these plugins for any development task.

---

## 🏗️ 1. GSD (Get Shit Done) Plugin
**Purpose**: Professional project governance and phased execution.
- **Location**: `.agent/workflows/gsd-*`
- **Usage**: 
  - `/gsd-plan`: Create detailed execution plans.
  - `/gsd-execute`: Follow a plan with strict validation.
  - `/gsd-map-codebase`: Index the project's technical architecture.

## 🤖 2. Ralph Pattern Plugin
**Purpose**: Autonomous loop tracking and persistent memory.
- **Location**: `prd.json`, `progress.txt`, `.agent/workflows/ralph-sync.md`
- **Usage**: 
  - Synchronize state after every iteration.
  - Ensures the AI knows exactly what is done and what is next.
  - Maintains a "Learnings Log" for consistent future performance.

## 🏛️ 3. Agno SaaS Plugin
**Purpose**: Multi-agent orchestration for enterprise scaling.
- **Location**: `backend/main.py`
- **Usage**: 
  - Supervisor-Analyst-Researcher synergy.
  - Decoupled client-server protocols for high-concurrency.

## 🧪 4. Elite Analytics Plugin
**Purpose**: Industrial-grade data processing.
- **Location**: `pro_insight_analyst.py` (legacy) or `backend/`
- **Capabilities**: 
  - IQR Outlier Removal.
  - Bayesian-style Correlation Analysis.
  - Linear Trend Forecasting.

---

## 🛠️ How to Add New Plugins
To add a new capability:
1. Create a markdown file in `.agent/workflows/[plugin-name].md`.
2. Define the workflow steps clearly.
3. Update this directory.
