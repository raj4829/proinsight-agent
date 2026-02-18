# 🧠 AGENTS.md: Project Memory & Internal Conventions

This file is a "living memory" for AI agents working on ProInsight. It contains discovered patterns, codebase gotchas, and architectural rules that must be followed every iteration.

---

## 🏛️ Architectural Rules
1. **SaaS Protocol**: Always keep the `frontend` logic-free. All intelligence must reside in `backend/main.py`.
2. **DuckDB Persistence**: Use `analytics.db` for local persistence and `MotherDuck` for cloud. NEVER rely purely on `:memory:` for the SaaS version.
3. **Supervisor Pattern**: The Supervisor is the lead. It must always coordinate with the Analyst and Researcher before finalizing an Executive Briefing.
4. **Strategy Hub Logic**: Comparative analysis requires at least one revenue-like column and one cost-like column per table to calculate ROI/ROAS.

## ⚠️ Discovered Gotchas
- **SQL Escaping**: Column names with spaces (e.g., "Revenue 2024") MUST be wrapped in double quotes in DuckDB.
- **Agent Hallucinations**: The Data Analyst sometimes guesses table names. Always run `SHOW TABLES` or check `schema_info` before generating SQL.
- **Port Conflicts**: Backend runs on `8000`, Frontend runs on `8501+`. The `LAUNCH_SAAS.bat` handles this sync.

## 🎨 Design System
- **Fonts**: Use 'Inter' for body and 'Roboto Mono' for metrics.
- **Colors**: Primary is `#0EA5E9`. Accent is `#10B981`.
- **CSS**: Use the variables defined in `CUSTOM_CSS` to maintain the Glassmorphism aesthetic.

---
*Generated via Ralph/GSD Plugin Hub*
