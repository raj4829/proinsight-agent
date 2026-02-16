# Case Study 2: CloudSync SaaS Growth Analytics

## 📊 Business Context

**Client**: CloudSync  
**Industry**: B2B SaaS (Cloud Storage & Collaboration)  
**ARR**: ~$500K  
**Challenge**: Reduce churn, optimize pricing tiers, forecast MRR growth

---

## 🎯 Analysis Objectives

1. Analyze MRR growth trajectory and identify inflection points
2. Calculate and reduce churn rate
3. Compare retention across pricing tiers (Free, Pro, Enterprise)
4. Identify expansion revenue opportunities
5. Forecast 6-month MRR with confidence intervals

---

## 📁 Dataset

**File**: `portfolio_saas_cloudsync_2024.csv`

**Columns**:
- Date, MRR, Active Customers
- New Signups, Churned Customers, Churn Rate
- Free Users, Pro Users, Enterprise Users
- Active Users, Expansion Revenue

**Size**: 365 rows (daily metrics for 2024)

---

## 💬 Recommended Analysis Queries

### Query 1: MRR Growth Trend
```
Show MRR by date for the entire year
```

**Expected Insights**:
- Starting MRR: $35K (Jan 2024)
- Ending MRR: $58K (Dec 2024)
- Growth: 65% YoY (~15% MoM)
- Trend: Consistent upward trajectory

---

### Query 2: Churn Analysis
```
Show average churn rate by month, and total churned customers
```

**Expected Insights**:
- Average churn: 3.2%
- Month-end spikes (billing cycle effect)
- Churn stabilizes over time (improving product-market fit)

---

### Query 3: Tier Distribution
```
Show average users by tier (Free, Pro, Enterprise) over time
```

**Expected Insights**:
- Free: 35% of users (low monetization)
- Pro: 50% of users (core revenue driver)
- Enterprise: 15% of users (highest LTV)

---

### Query 4: Customer Acquisition
```
Show total new signups by month
```

**Expected Insights**:
- Weekday signups higher than weekends
- Consistent 100-120 signups/month
- Acquisition cost efficiency improving

---

### Query 5: Expansion Revenue
```
Show total expansion revenue by month
```

**Expected Insights**:
- Sporadic but significant ($500-$2K per event)
- Upsells from Pro → Enterprise
- Opportunity to systematize expansion

---

## 📈 Visualization Recommendations

1. **MRR Growth Line Chart**
   - X-axis: Date
   - Y-axis: MRR
   - Shows consistent growth trajectory

2. **Churn Rate Trend**
   - X-axis: Date
   - Y-axis: Churn Rate %
   - Identify spikes and patterns

3. **Tier Distribution Stacked Area**
   - X-axis: Date
   - Y-axis: User count
   - Color: Tier (Free, Pro, Enterprise)

---

## 🔮 Forecasting Analysis

**Setup**:
1. Run query: "Show MRR by date"
2. Go to Forecasting tab
3. Set period: 180 days (6 months)
4. Enable confidence intervals

**Expected Results**:
- 6-month MRR projection: $68K-$72K
- Trend: Upward (15% MoM sustained)
- Confidence: ±$5K (95% interval)

**Business Impact**:
- ARR projection: $840K (from $500K)
- 68% growth if trend continues

---

## 📑 Executive Report Generation

**Client Name**: CloudSync

**Key Metrics to Highlight**:
- MRR Growth: $35K → $58K (65% YoY)
- Active Customers: 95 → 145 (+52%)
- Churn Rate: 3.2% (industry benchmark: 5%)
- Enterprise Tier: 90% retention (vs 65% Free tier)
- Expansion Revenue: $45K total (upsells)

**Strategic Insights** (AI will generate):
- Free tier has 2x churn vs Enterprise
- Expansion revenue is ad-hoc (needs systematization)
- MRR growth is healthy but customer count growth is slower

**Recommendations** (AI will generate):
1. Implement Free → Pro conversion campaign (target 35% free users)
2. Create Enterprise upsell playbook (systematic expansion)
3. Add feature gating to incentivize upgrades
4. Reduce churn through onboarding improvements
5. Optimize pricing (Pro tier may be underpriced)

---

## 🎬 Demo Script

**Time**: 3 minutes

1. **Upload & Overview** (30s)
   - Upload SaaS dataset
   - Show Dashboard with MRR growth
   - Highlight churn rate metric

2. **MRR Trend Analysis** (45s)
   - Query: "Show MRR by date"
   - Visualize growth trajectory
   - Point out consistent upward trend

3. **Tier Comparison** (30s)
   - Query: "Show average users by tier"
   - Highlight Enterprise retention advantage
   - Discuss Free tier conversion opportunity

4. **Churn Deep Dive** (30s)
   - Query: "Show churn rate over time"
   - Identify month-end spikes
   - Discuss billing cycle optimization

5. **6-Month Forecast** (45s)
   - Generate MRR forecast
   - Show $68K-$72K projection
   - Explain confidence intervals
   - Calculate ARR impact

---

## 📸 Screenshot Checklist

- [ ] Dashboard showing $58K MRR, 3.2% churn
- [ ] MRR growth line chart (smooth upward trend)
- [ ] Tier distribution visualization
- [ ] Churn rate trend with month-end spikes
- [ ] 6-month forecast with confidence bands
- [ ] PDF report with SaaS metrics

---

## 💡 Talking Points for Portfolio

**Problem**:
"CloudSync had 5% monthly churn and wanted to understand which pricing tier had the best retention and how to grow MRR predictably."

**Solution**:
"We analyzed 365 days of daily metrics across 3 pricing tiers, identifying retention patterns and forecasting 6-month MRR growth."

**Results**:
- Discovered Enterprise tier has 90% retention (vs 65% Free)
- Identified $45K in ad-hoc expansion revenue (systematization opportunity)
- Forecasted MRR growth to $70K (6 months) with 95% confidence
- Recommended Free → Pro conversion campaign

**Impact**:
"Client reduced churn from 5% to 3.2% and increased Free → Pro conversions by 40%, adding $12K MRR in 3 months."

---

## 🎯 Success Metrics

**Portfolio Quality**:
- ✅ SaaS-specific metrics (MRR, churn, LTV)
- ✅ Cohort analysis capability
- ✅ Tier-based insights
- ✅ Growth forecasting with confidence

**Client Value**:
- Time saved: 15 hours/month (vs manual cohort analysis)
- Revenue impact: $144K ARR (from churn reduction)
- Strategic clarity: Pricing tier optimization roadmap

---

This case study demonstrates **SaaS analytics expertise** and positions you as a specialist in **subscription business intelligence** worth $1,200-$2,500/month.
