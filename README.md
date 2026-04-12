# 📊 CampaignIQ — Marketing Campaign Attribution & ROI Analytics

**CampaignIQ** is a production-style analytics package that turns raw campaign rows into **attribution**, **ROI**, **segment insights**, **statistical testing**, and **budget reallocation** guidance — plus an interactive **Streamlit** dashboard for ongoing monitoring.

---

## 🎯 Business problem

Marketing teams need to know **which channels and campaigns actually fund growth**, not just which ones spend the most. Weak attribution creates three expensive failures: budgets follow habit instead of performance, high-value audiences stay under-invested, and leadership sees activity metrics instead of profit logic. CampaignIQ connects **spend → modeled revenue → ROI → segments → tests → budget scenarios** so decisions are evidence-led and finance-ready.

---

## 🔎 Representative findings (placeholders — run the notebook on your CSV)

| Metric | Example headline (your run may differ) |
| --- | --- |
| Overall ROI | **~420–520%** portfolio ROI (modeled from spend + ROI field) |
| Best channel (typical) | Often **YouTube** or **Google Ads** on efficiency in this dataset |
| Reallocation lift (directional) | **+1% to +6%** modeled revenue under efficiency-weighted mix (same total spend) |
| Segment pockets | **Tech Enthusiasts** / **Health & Wellness** frequently show strong intersections |

> These are **illustrative** ranges; execute `CampaignIQ_Analysis.ipynb` locally for exact numbers.

---

## 🧰 Tools & stack

| Layer | Tooling |
| --- | --- |
| Data prep | `pandas`, `numpy` |
| Analysis & statistics | `scipy`, `statsmodels` |
| Static storytelling | `matplotlib`, `seaborn` |
| Interactive BI | `plotly`, `streamlit` |
| Notebook | `jupyter`, `ipykernel` |

---

## 🚀 How to run

### 1) Environment

```bash
cd campaigniq-marketing-analytics
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Data

Place **`marketing_data.csv`** next to the notebook and dashboard (this repo ships a copy sourced from the workspace marketing extract).

**Columns used (actual schema):**  
`Campaign_ID`, `Company`, `Campaign_Type`, `Target_Audience`, `Duration`, `Channel_Used`, `Conversion_Rate`, `Acquisition_Cost`, `ROI`, `Location`, `Language`, `Clicks`, `Impressions`, `Engagement_Score`, `Customer_Segment`, `Date`

Engineered fields: **Spend** (cleaned `Acquisition_Cost`), **Revenue** = `Spend × (1 + ROI/100)`, **Conversions** = `Conversion_Rate × Clicks`.

### 3) Notebook

```bash
jupyter notebook CampaignIQ_Analysis.ipynb
```

### 4) Dashboard

```bash
streamlit run dashboard.py
```

Open the local URL Streamlit prints (defaults to **http://localhost:8501**).

---

## 📁 Project structure

```
campaigniq-marketing-analytics/
├── CampaignIQ_Analysis.ipynb   # End-to-end analysis + executive narrative
├── dashboard.py                # Streamlit monitoring app
├── requirements.txt            # Locked dependency baseline (semver ranges)
├── README.md                   # You are here
└── marketing_data.csv          # Campaign-level marketing dataset
```

---

## 🧭 What the dashboard shows

- **Sidebar filters:** campaign type, date range, channels, audience segment  
- **KPI row:** total spend, total revenue, overall ROI %, best channel by ROI  
- **Charts:** channel ROI bars, spend vs revenue scatter (bubble = conversions), monthly trends, segment×channel heatmap, budget mix (current vs recommended), top campaigns table  

---

## 📝 Notes for stakeholders

- ROI and revenue are **modeled from the dataset’s ROI definition** to enable consistent channel comparisons; finance should align definitions with accounting before using outputs as official targets.
- A/B testing uses a **practical proxy** when explicit experiment flags are absent (two campaign types compared with a two-proportion z-test on pooled clicks).
- Budget “lift” is a **scenario model**, not a promise — validate with incrementality or geo holdouts before large reallocations.

---

Built for marketing, analytics, and growth teams who want **one coherent story** from spreadsheet to dashboard.
