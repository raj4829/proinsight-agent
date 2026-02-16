# 🚀 ProInsight Agency Platform: Setup & Run Guide

This comprehensive guide will help you set up and run the ProInsight Agency Analytics Platform on your local machine.

---

## ✅ Prerequisites

### 1. Python Installation
**Required Version**: Python 3.10 or higher

**Check your version:**
```powershell
python --version
```

**If not installed:**
- Download from [python.org](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"

### 2. OpenAI API Key
You need an active OpenAI API key to power the AI agent.

**Get your key:**
1. Visit [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Copy and save it securely (you'll need it in the app)

**Check your credits:**
- Visit [platform.openai.com/usage](https://platform.openai.com/usage)
- Ensure you have available balance

---

## ⚡ Installation Methods

### Option 1: One-Click Launch (Windows Only)

The fastest way to get started:

1. Navigate to the project folder in File Explorer
2. **Double-click** `run_analyst.bat`
3. Wait for dependencies to install
4. Browser will auto-open at `http://localhost:8501`

**What the script does:**
```batch
pip install -r requirements.txt
streamlit run pro_insight_analyst.py
```

---

### Option 2: Manual Setup (All Platforms)

#### Step 1: Open Terminal

**Windows:**
- Press `Win + R`, type `cmd`, press Enter
- Or use PowerShell

**Mac/Linux:**
- Press `Cmd + Space`, type "Terminal"
- Or use your preferred terminal emulator

#### Step 2: Navigate to Project Directory

```bash
cd path/to/awesome-llm-apps/starter_ai_agents/ai_data_analysis_agent
```

**Example (Windows):**
```powershell
cd C:\Users\YourName\Downloads\awesome-llm-apps-main\awesome-llm-apps-main\starter_ai_agents\ai_data_analysis_agent
```

#### Step 3: Create Virtual Environment (Recommended)

**Why?** Keeps dependencies isolated from other Python projects.

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**You'll see** `(venv)` prefix in your terminal when activated.

#### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed streamlit-1.x.x pandas-2.x.x duckdb-0.x.x agno-2.x.x ...
```

**If you see errors:**
```bash
# Try upgrading pip first
python -m pip install --upgrade pip

# Then retry
pip install -r requirements.txt
```

#### Step 5: Launch the Application

```bash
streamlit run pro_insight_analyst.py
```

**Expected output:**
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**Browser doesn't open automatically?**
- Manually navigate to `http://localhost:8501`

---

## 📖 Using the Application

### Initial Setup

1. **Enter API Key**
   - Look at the left sidebar
   - Find "OpenAI API Key" input field
   - Paste your key (starts with `sk-...`)
   - Key is stored in session only (not saved to disk)

2. **Upload Data**
   - Click "Browse files" under "Data Sources"
   - Select one or more files:
     - `sample_sales_data.csv` (included)
     - `sample_ad_spend.csv` (included)
     - Your own CSV/Excel files
   - Files are loaded into DuckDB automatically

3. **Verify Upload**
   - Check "Active Tables" section in sidebar
   - You should see your table names with row counts

---

### Feature Walkthroughs

#### 💬 Deep Query (Natural Language SQL)

**Purpose**: Ask questions about your data without writing SQL.

**Example Queries:**
```
"Show total revenue by product"
"What are the top 5 dates by sales?"
"Join sales and ad_spend on Date. Calculate ROAS."
```

**How it works:**
1. Type your question in the text area
2. Click "🚀 Run Analysis"
3. AI generates SQL query (shown in expandable section)
4. Results appear as a table

---

#### 📈 Interactive Viz (Plotly Charts)

**Purpose**: Visualize query results with interactive charts.

**Steps:**
1. Run a query in "Deep Query" tab first
2. Switch to "Interactive Viz" tab
3. Chart auto-generates based on data types:
   - **Date + Number** → Line chart
   - **Category + Number** → Bar chart
   - **Number + Number** → Scatter plot

**Interactions:**
- Hover for tooltips
- Click and drag to zoom
- Double-click to reset
- Click camera icon to download PNG

---

#### 🔮 Future Forecast (Predictive Analytics)

**Purpose**: Project future trends using machine learning.

**Requirements:**
- Query result must have at least one date column
- Query result must have at least one numeric column

**Steps:**
1. Run a time-series query (e.g., "Show revenue by date")
2. Switch to "Future Forecast" tab
3. Adjust "Days to Predict" slider (7-365)
4. Click "Generate Forecast"
5. View combined Actual + Forecast chart

**Use Cases:**
- Revenue forecasting
- Inventory planning
- Trend analysis

---

#### 📑 Client Reporting (PDF Generation)

**Purpose**: Create professional, branded PDF reports for clients.

**Steps:**
1. Ensure you have uploaded data
2. Go to "Client Reporting" tab
3. Enter client name (e.g., "TechCorp")
4. Click "✨ Generate Agency-Grade Report"
5. Wait for AI to analyze data (~10-30 seconds)
6. Review metrics and strategy preview
7. Click "📥 Download Professional PDF"

**PDF Contents:**
- **Section 1**: Key Performance Indicators (calculated metrics)
- **Section 2**: Executive Analysis (AI interpretation)
- **Section 3**: Strategic Recommendations (actionable steps)

---

## 🔧 Advanced Configuration

### Change OpenAI Model

Edit `pro_insight_analyst.py` line 267:
```python
model=OpenAIChat(id="gpt-4o-mini", api_key=...)  # Cheaper model
```

### Enable Persistent Database

Edit `pro_insight_analyst.py` line 41:
```python
st.session_state["duckdb_con"] = duckdb.connect(database="analytics.db")
```

### Customize PDF Branding

Edit `pro_insight_analyst.py` lines 150-157 to change:
- Title text
- Colors (RGB values)
- Font sizes

---

## ❓ Troubleshooting

### Issue: "Command not found: streamlit"

**Cause**: Dependencies not installed or PATH issue.

**Fix:**
```bash
# Verify installation
pip list | grep streamlit

# If missing
pip install streamlit

# If still fails (Windows)
python -m streamlit run pro_insight_analyst.py
```

---

### Issue: "ModuleNotFoundError: No module named 'agno'"

**Cause**: Agno library not installed.

**Fix:**
```bash
pip install --upgrade agno
```

---

### Issue: "Table not found" Error

**Cause**: Streamlit session reset or file not uploaded.

**Fix:**
1. Check sidebar "Active Tables" section
2. If empty, re-upload your files
3. If still failing, click "🗑️ Reset Workspace" and start fresh

---

### Issue: "OpenAI API Error: Rate Limit"

**Cause**: Too many requests or insufficient credits.

**Fix:**
1. Check usage at [platform.openai.com/usage](https://platform.openai.com/usage)
2. Add credits if needed
3. Wait a few minutes before retrying

---

### Issue: Charts Not Displaying

**Cause**: Plotly library issue.

**Fix:**
```bash
pip install --upgrade plotly
# Restart Streamlit
```

---

### Issue: PDF Download Fails

**Cause**: FPDF encoding issue with special characters.

**Fix:**
- Avoid emojis or special Unicode in client names
- Use ASCII characters only (A-Z, 0-9)

---

## 🧪 Testing Your Setup

Follow the **TESTING_GUIDE.md** for a complete feature verification checklist.

**Quick Test:**
1. Upload `sample_sales_data.csv`
2. Ask: "Show total revenue"
3. Expected: Table with sum of Revenue column
4. If this works, your setup is correct!

---

## 🚀 Next Steps

Once the app is running:

1. **Read TESTING_GUIDE.md**: Verify all 4 phases work
2. **Read PROJECT_OVERVIEW.md**: Understand monetization strategies
3. **Read SYSTEM_ARCHITECTURE.md**: Learn the technical architecture

---

## 📞 Getting Help

**If you're stuck:**
1. Check the troubleshooting section above
2. Review error messages carefully
3. Verify all prerequisites are met
4. Check that you're using Python 3.10+

**Common mistakes:**
- Forgetting to activate virtual environment
- Using Python 2.x instead of 3.x
- Not installing dependencies
- Invalid or expired OpenAI API key

---

**Ready to build your Agency Platform? Let's go! 🚀**
