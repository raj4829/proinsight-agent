# 🔧 ProInsight Troubleshooting Guide

## Common Issues & Solutions

### Issue 1: "Column Not Found" Error with Spaces in Column Names

**Error Message:**
```
Binder Error: Values list "ssd" does not have a column named "Units_Sold"
```

**Root Cause:**
The AI agent generated SQL using `Units_Sold` (underscore) when the actual column name is `Units Sold` (space).

**Solution Applied (v2.0):**
The agent now receives column names with proper quoting in the schema:
```
Before: Columns ['Date', 'Product', 'Units Sold']
After:  Columns [Date, Product, "Units Sold"]
```

**Updated Agent Instructions:**
- "Column names with spaces MUST be wrapped in double quotes"
- Schema now shows quoted column names automatically

**Correct SQL Pattern:**
```sql
SELECT 
    ssd."Units Sold",  -- ✅ Correct
    ssd.Date,          -- ✅ No quotes needed (no spaces)
    ssd.Product
FROM sample_sales_data ssd
```

**Incorrect SQL Pattern:**
```sql
SELECT 
    ssd.Units_Sold,    -- ❌ Wrong (underscore instead of space)
    ssd.Units Sold     -- ❌ Wrong (no quotes)
FROM sample_sales_data ssd
```

---

### Issue 2: "Table Not Found" Error

**Error Message:**
```
Catalog Error: Table with name "sample_sales_data" does not exist
```

**Root Cause:**
- File not uploaded
- Session state cleared
- DuckDB connection lost

**Solution:**
1. Check sidebar "Active Tables" section
2. If empty, re-upload your CSV/Excel files
3. If still failing, click "🗑️ Reset Workspace" and start fresh

---

### Issue 3: Agent Returns Text Instead of SQL

**Error Message:**
No error, but the agent writes explanatory text instead of generating a query.

**Root Cause:**
The prompt was too vague or conversational.

**Solution:**
Be explicit in your requests:

**❌ Vague:**
```
"Tell me about the sales"
```

**✅ Explicit:**
```
"Show total revenue by product"
"Calculate profit by date"
"Join sales and ad_spend tables on Date"
```

---

### Issue 4: JOIN Query Fails

**Error Message:**
```
Binder Error: Referenced column "Date" not found in FROM clause
```

**Root Cause:**
Ambiguous column reference when multiple tables have the same column name.

**Solution:**
Always use table aliases in JOINs:

**❌ Ambiguous:**
```sql
SELECT Date, Revenue, Ad_Spend
FROM sample_sales_data
JOIN sample_ad_spend ON Date = Date  -- Which Date?
```

**✅ Clear:**
```sql
SELECT 
    ssd.Date,
    ssd.Revenue,
    sas.Ad_Spend
FROM sample_sales_data ssd
JOIN sample_ad_spend sas ON ssd.Date = sas.Date
```

---

### Issue 5: Forecasting Fails

**Error Message:**
```
"Need at least one Date column and one Numeric column"
```

**Root Cause:**
Your query result doesn't have the required column types.

**Solution:**
Ensure your query returns:
1. At least one `datetime` column (e.g., Date)
2. At least one `numeric` column (e.g., Revenue, Profit)

**Example Working Query:**
```sql
SELECT Date, SUM(Revenue) AS Total_Revenue
FROM sample_sales_data
GROUP BY Date
ORDER BY Date
```

---

### Issue 6: PDF Generation Fails with Unicode Error

**Error Message:**
```
UnicodeEncodeError: 'latin-1' codec can't encode character
```

**Root Cause:**
FPDF library has limited Unicode support. Special characters (emojis, non-ASCII) in client names or AI-generated text cause encoding errors.

**Solution:**
1. Use ASCII-only client names (A-Z, 0-9, spaces)
2. Avoid emojis in prompts
3. The app automatically sanitizes text using `unicodedata.normalize()`

**❌ Problematic:**
```
Client Name: "TechCorp™ 🚀"
```

**✅ Safe:**
```
Client Name: "TechCorp"
```

---

### Issue 7: Slow Query Performance

**Symptom:**
Queries take > 5 seconds to execute.

**Root Cause:**
- Large dataset (> 100K rows)
- Complex JOIN without indexes
- Inefficient GROUP BY

**Solution:**
1. **Add LIMIT clause** for testing:
   ```sql
   SELECT * FROM large_table LIMIT 1000
   ```

2. **Use DuckDB's QUALIFY** for window functions:
   ```sql
   SELECT *, ROW_NUMBER() OVER (PARTITION BY Product ORDER BY Revenue DESC) AS rn
   FROM sample_sales_data
   QUALIFY rn <= 10  -- Top 10 per product
   ```

3. **Switch to persistent DuckDB** (see SYSTEM_ARCHITECTURE.md):
   ```python
   # In pro_insight_analyst.py, line 41
   st.session_state["duckdb_con"] = duckdb.connect("data.db")
   ```

---

### Issue 8: Charts Not Displaying

**Symptom:**
"Interactive Viz" tab shows "Run a query first" even after running a query.

**Root Cause:**
`st.session_state["last_result"]` not set.

**Solution:**
1. Ensure you clicked "🚀 Run Analysis" button
2. Check that query returned results (not empty DataFrame)
3. Refresh the page and try again

---

### Issue 9: OpenAI Rate Limit Error

**Error Message:**
```
RateLimitError: You exceeded your current quota
```

**Root Cause:**
- No credits in OpenAI account
- Too many requests in short time
- Using free tier with limits

**Solution:**
1. Check usage: [platform.openai.com/usage](https://platform.openai.com/usage)
2. Add credits: [platform.openai.com/billing](https://platform.openai.com/billing)
3. Wait 60 seconds between requests if on free tier

---

### Issue 10: Multiple Files Not Showing in Active Tables

**Symptom:**
Uploaded 3 files but only 1 shows in "Active Tables".

**Root Cause:**
Files have the same name (e.g., all named "data.csv").

**Solution:**
Rename files to unique names before uploading:
```
sales_2024.csv
sales_2023.csv
ad_spend_2024.csv
```

The app sanitizes names to lowercase with underscores:
```
sales_2024.csv → sample_sales_2024
ad_spend_2024.csv → sample_ad_spend_2024
```

---

## Quick Diagnostic Checklist

When something goes wrong, check these in order:

1. ✅ **API Key Valid?** - Check sidebar input
2. ✅ **Files Uploaded?** - Check "Active Tables" section
3. ✅ **Query Has Results?** - Check row count in success message
4. ✅ **Column Names Correct?** - Check schema in sidebar
5. ✅ **SQL Syntax Valid?** - Click "Show SQL" to review
6. ✅ **Browser Console Errors?** - Press F12 to check

---

## Getting Help

If none of these solutions work:

1. **Check the error message carefully** - It usually tells you exactly what's wrong
2. **Review SYSTEM_ARCHITECTURE.md** - Understand the data flow
3. **Test with sample files** - Verify the app works with `sample_sales_data.csv`
4. **Reset workspace** - Click "🗑️ Reset Workspace" for a clean slate

---

## Version History

**v2.0** (2026-02-15):
- ✅ Fixed column name quoting for spaces
- ✅ Enhanced agent instructions
- ✅ Improved schema formatting

**v1.0** (2026-02-14):
- Initial release with multi-file support
- Forecasting and PDF reporting

---

**Last Updated**: 2026-02-15  
**Maintained By**: Lead Solutions Architect
