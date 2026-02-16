# 📊 ProInsight Agency Platform

An **Agency-Grade AI Data Analysis Platform** built using the Agno Agent framework and OpenAI's GPT-4o model. This platform enables consultants and agencies to upload multiple datasets, perform complex SQL analysis with JOINs, predict future trends with forecasting, and generate professional white-label PDF reports.

## 🌟 Key Features

### 📂 Multi-File Data Hub
- Upload multiple CSV and Excel files simultaneously
- Automatic date parsing and table registration
- AI-powered JOIN queries across datasets
- Support for complex multi-table analysis

### 📈 Interactive Visualizations
- **Plotly-powered charts** with zoom, pan, and export capabilities
- Auto-detection of optimal chart types (Line, Bar, Scatter)
- Dynamic axis customization
- Professional, client-ready visuals

### 🔮 AI Forecasting Engine
- **Predictive Analytics** using Scikit-Learn Linear Regression
- Time-series projections (7-365 days)
- Visual comparison of "Actual vs Forecast" data
- Automatic trend detection

### 📑 White-Label PDF Reporting
- **Calculated Metrics**: Auto-extracts Total Revenue, ROI, Ad Spend
- **AI Strategy**: Generates Executive Analysis and Recommendations
- **Professional PDFs**: Structured reports ready for client delivery
- Branded output with custom client names

### 💬 Natural Language SQL Generation
- Convert questions into DuckDB SQL queries
- No SQL knowledge required
- Secure execution (no arbitrary code)
- Full query auditability

## 🏗️ Technical Architecture

**Framework Stack:**
- **Agno**: Agentic AI framework for SQL generation
- **Streamlit**: Interactive web UI
- **DuckDB**: High-performance OLAP database
- **Plotly**: Interactive visualizations
- **Scikit-Learn**: Machine learning forecasting
- **FPDF**: PDF report generation

**Design Pattern:**
- **SQL Generator Pattern**: AI writes SQL → App executes safely
- **No Direct Code Execution**: Security-first architecture
- **Session State Management**: Persistent DuckDB connections

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

### Installation

**Option 1: One-Click (Windows)**
```bash
# Double-click run_analyst.bat
```

**Option 2: Manual Setup**
```bash
# Clone repository
git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git
cd awesome-llm-apps/starter_ai_agents/ai_data_analysis_agent

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run pro_insight_analyst.py
```

### First Use
1. Open browser at `http://localhost:8501`
2. Enter your OpenAI API Key in the sidebar
3. Upload sample files (`sample_sales_data.csv`, `sample_ad_spend.csv`)
4. Start analyzing!

## 📖 Usage Examples

### Multi-Table Analysis
```
User: "Join sales and ad_spend on Date. Show Revenue and Ad_Spend by Date."
AI: Generates SQL JOIN query → Returns combined dataset
```

### Forecasting
```
1. Query: "Show total revenue by date"
2. Switch to "Future Forecast" tab
3. Set prediction period (e.g., 30 days)
4. View Actual vs Forecast chart
```

### PDF Report Generation
```
1. Go to "Client Reporting" tab
2. Enter client name (e.g., "TechCorp")
3. Click "Generate Agency-Grade Report"
4. Download professional PDF with metrics + strategy
```

## 💰 Monetization Strategies

### 1. Freelance Data Consultant
- **Platform**: Upwork, Fiverr
- **Service**: "Executive BI Dashboards & Forecasts"
- **Rate**: $50-$150 per report
- **Time**: 5-10 minutes per report

### 2. White-Label Agency Partner
- **Target**: Small marketing agencies
- **Offer**: Handle all client reporting
- **Rate**: $500-$2000/month retainer
- **Value**: Agencies outsource their pain point

### 3. Micro-SaaS
- **Model**: Subscription-based web app
- **Price**: $29-$99/month
- **Requirements**: Add authentication + Stripe integration
- **Scalability**: Recurring revenue

## 📁 Project Structure

```
ai_data_analysis_agent/
├── pro_insight_analyst.py      # Main application
├── requirements.txt            # Python dependencies
├── run_analyst.bat            # Windows launcher
├── sample_sales_data.csv      # Demo dataset
├── sample_ad_spend.csv        # Demo dataset
├── README.md                  # This file
├── RUN_INSTRUCTIONS.md        # Detailed setup guide
├── TESTING_GUIDE.md           # Feature verification
├── PROJECT_OVERVIEW.md        # Architecture overview
└── SYSTEM_ARCHITECTURE.md     # Technical deep-dive
```

## 🔧 Configuration

### Environment Variables (Optional)
```bash
# Set default OpenAI key (not recommended for production)
export OPENAI_API_KEY="sk-..."
```

### DuckDB Settings
The application uses in-memory DuckDB by default. For persistent storage:
```python
# In pro_insight_analyst.py, line 41
st.session_state["duckdb_con"] = duckdb.connect(database="data.db")
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'agno'"
```bash
pip install --upgrade agno
```

### "Table not found" Error
- Ensure files are uploaded in the sidebar
- Check "Active Tables" section shows your data
- Re-upload files if session was reset

### "OpenAI Rate Limit"
- Verify API key has credits
- Check usage at [platform.openai.com](https://platform.openai.com/usage)

### Charts Not Displaying
```bash
pip install --upgrade plotly
```

## 📚 Documentation

- **[RUN_INSTRUCTIONS.md](RUN_INSTRUCTIONS.md)**: Step-by-step setup
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)**: Feature verification checklist
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)**: Business context
- **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)**: Technical deep-dive

## 🤝 Contributing

This is a reference implementation. To extend:

1. **Add Custom Tools**: See `SYSTEM_ARCHITECTURE.md` Section 8.2
2. **Implement RAG**: Add `AgentKnowledge` for document Q&A
3. **Advanced Forecasting**: Replace Linear Regression with Prophet/ARIMA

## 📄 License

MIT License - See repository root for details

## 🙏 Acknowledgments

- **Agno Framework**: [github.com/agno-ai](https://github.com/agno-ai)
- **Streamlit**: [streamlit.io](https://streamlit.io)
- **DuckDB**: [duckdb.org](https://duckdb.org)

## 📞 Support

For issues or questions:
1. Check `TROUBLESHOOTING` section above
2. Review `SYSTEM_ARCHITECTURE.md` for technical details
3. Open an issue in the main repository

---

**Built with ❤️ using Agno + OpenAI + DuckDB**
