# Coding Conventions

## UI/UX: Pro Max System
- **Style**: Enterprise Minimal / Elite Consulting.
- **Colors**: Deep Ocean SaaS palette (#0EA5E9, #0F172A).
- **Typography**: Inter (UI) and Roboto Mono (Data/Metrics).
- **Components**: Bento Grid metric cards, Glassmorphism-lite insight boxes.

## Code Patterns
- **State Management**: Streamlit `session_state` for all reactive variables.
- **SQL Safety**: Use `double quotes` for column names with spaces.
- **Error Handling**: Try-except blocks around SQL execution and file loading with user-facing error messages.
- **Modularity**: Currently centralized in `pro_insight_analyst.py` to maintain single-file portability as requested by user.
