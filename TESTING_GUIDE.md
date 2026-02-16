# 🧪 ProInsight Analyst: Testing Guide

This guide will help you verify that your new Agency-Level features are working correctly.

## 🛠️ Setup
1.  Ensure the app is running: `http://localhost:8505` (or similar port).
2.  Have your API Key ready.
3.  Located sample files: `sample_sales_data.csv` and `sample_ad_spend.csv` in the project folder.

---

## 🏗️ Phase 1: Multi-File & Joins

**Goal**: Verify we can upload multiple files and join them in a query.

1.  **Upload**: Go to the sidebar and upload **BOTH** `sample_sales_data.csv` and `sample_ad_spend.csv`.
2.  **Verify**: Check the sidebar. You should see "Active Tables" listing both files.
3.  **Test Query**: Go to "Deep Query" tab and ask:
    > "Join sample_sales_data and sample_ad_spend on Date using an inner join. Show the total revenue and total ad spend by date."
4.  **Success**: You should see a table with `Date`, `Revenue` (from sales), and `Ad_Spend` (from ads).

---

## 📈 Phase 2: Interactive Viz

**Goal**: Verify Plotly charts work.

1.  **Run Query**: Ask "Show revenue by product" in "Deep Query".
2.  **Switch Tab**: Click "Interactive Viz".
3.  **Test**:
    *   You should see a Bar Chart automatically appear.
    *   Hover over the bars to see tooltips.
    *   Click the "Camera" icon (top right of chart) to download it as PNG (simulating export).

---

## 🔮 Phase 3: Forecasting

**Goal**: Predict future revenue.

1.  **Run Time-Series Query**: Ask "Show total revenue by date" in "Deep Query".
2.  **Switch Tab**: Click "Future Forecast".
3.  **Configure**: Set "Days to Predict" to `30`.
4.  **Run**: Click "Generate Forecast".
5.  **Success**: You should see a line chart with a new "Forecast" line extending into the future.

---

## 📑 Phase 4: PDF Reporting

**Goal**: Generate a white-label PDF.

1.  **Switch Tab**: Click "Client Reporting".
2.  **Enter Name**: Type "TechCorp" as Client Name.
3.  **Run**: Click "Generate PDF Brief".
4.  **Wait**: The AI will write a summary.
5.  **Download**: Click the "Download PDF Report" button and open the file.
    *   Check for the Title "Executive Data Report: TechCorp".
    *   Check for the Date and the AI-generated text.

---

## ✅ Final Check
If all 4 phases pass, your application is fully production-ready for an Agency use case!
