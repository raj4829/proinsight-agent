# 📱 Mobile Access & 🚀 Cloud Deployment Guide

This guide explains how to access **ProInsight** on your phone right now and how to deploy it to the cloud for a professional portfolio link.

---

## 📱 1. Accessing on Your Phone (Same WiFi)

If your computer and phone are on the same WiFi network, follow these steps:

1.  **Find your Network URL**: 
    Look at the terminal where Streamlit is running. It should look like this:
    - **Local URL**: `http://localhost:8507`
    - **Network URL**: `http://192.168.29.160:8507` (Your exact numbers may vary)

2.  **Open Phone Browser**: 
    Type the **Network URL** (e.g., `http://192.168.29.160:8507`) into Chrome or Safari on your phone.

3.  **Troubleshooting (If it doesn't load)**:
    Windows often blocks "Incoming Connections".
    - Go to **Windows Security** > **Firewall & network protection**.
    - Click **Allow an app through firewall**.
    - Find `python.exe` or `Streamlit` and ensure **Private** and **Public** are checked.
    - Alternatively, temporarily disable your Private Firewall for 5 minutes to test.

---

## 🚀 2. Professional Cloud Deployment (Free)

To get a link like `raj-proinsight.streamlit.app` that works anywhere:

### Step A: Push to GitHub
1.  Create a new repository on [GitHub](https://github.com/new) called `proinsight-agent`.
2.  In your project folder, run:
    ```bash
    git init
    git add .
    git commit -m "Initial portfolio commit"
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/proinsight-agent.git
    git push -u origin main
    ```

### Step B: Connect to Streamlit Cloud
1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Click **Create app** > **Yup, I have an app**.
3.  Select your `proinsight-agent` repository and `pro_insight_analyst.py` as the main file.

### Step C: Configure Secrets (CRITICAL)
Your app needs the OpenAI key to work in the cloud:
1.  In the Streamlit Cloud dashboard, click **Settings** for your app.
2.  Go to **Secrets**.
3.  Add your key in this format:
    ```toml
    OPENAI_API_KEY = "your-key-here"
    ```
4.  The app will automatically detect this and restart.

---

## 🔥 3. Mobile UI Features

The platform is now optimized for mobile:
- **Responsive Layout**: Metric cards stack vertically on phones.
- **Large Touch Targets**: Buttons scale to full width for easy tapping.
- **Optimized Fonts**: Headers shrink to fit small screens without overlapping.
- **Interactive Charts**: Plotly charts support pinch-to-zoom and touch-pan.

---

## 💰 Why Deployment Matters for a $500 Project
- **Instant Access**: Clients can open your portfolio during a meeting on their phone.
- **Credibility**: Having a custom `.streamlit.app` or custom domain url looks professional.
- **Reliability**: No need to keep your laptop running for clients to see the results.

---
*Created for Raj Singh - Lead Solutions Architect*
