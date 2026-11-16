# 🚀 StartupLens AI: Indian Startup Ecosystem Valuation, Funding Dynamics & Investor Intelligence System

**Author:** Dhruval | **Course:** Artificial Intelligence & Machine Learning (AIML)  
**Production Stack:** FastAPI • Scikit-Learn • HTML5/CSS3/Vanilla JS • Chart.js • Streamlit  
**Dataset:** 3,044 Verified Indian Venture Capital Transactions across 2015–2020+ (\$46.37B Deployed)

---

## 📌 Executive Project Overview
**StartupLens AI** is an enterprise-grade Artificial Intelligence and Machine Learning decision-support platform designed to analyze, benchmark, and predict venture capital funding rounds across the Indian startup ecosystem.

Derived from exhaustive exploratory data analysis, feature engineering, and hyperparameter-tuned ensemble modeling in `Dhruval_AIML_Project.ipynb`, this application transitions theoretical data science research into a production-grade full-stack system comprising:
1. **High-Performance FastAPI REST API Backend** (`backend/app.py`): Scalable endpoints for real-time model inference, counterfactual scenario simulation, sector ranking, and investor intelligence.
2. **Interactive Glassmorphic Web Dashboard** (`frontend/`): Responsive, cyber-fintech UI equipped with real-time parameter tuning, confidence meters, What-If geographical comparisons, and Chart.js visualizations.
3. **Dual-Mode Streamlit Dashboard** (`streamlit_app.py`): An alternate full-featured presentation dashboard optimized for academic viva, live demos, and research evaluations.

---

## 🏗️ System Architecture & Directory Structure

```
d:\CLG\Dhruval\
├── backend\
│   ├── __init__.py
│   ├── app.py                      # FastAPI REST application & endpoint controllers
│   ├── config.py                   # Constants, currency exchange, paths, benchmark tables
│   ├── data_processor.py           # Robust dataset loader, cleaning & analytics engine
│   ├── ml_service.py               # ML inference, confidence bounds & what-if simulator
│   └── schemas.py                  # Pydantic data schemas for request/response validation
├── frontend\
│   ├── static\
│   │   ├── css\
│   │   │   └── style.css           # Glassmorphism dark/cyber UI styles & responsive grid
│   │   └── js\
│   │       └── app.js              # Client-side controller, Chart.js integrations & API calls
│   └── templates\
│       └── index.html              # Single-page web application UI
├── startup_funding_predictor.joblib # Serialized Gradient Boosting Pipeline artifact
├── startup_funding.csv             # Source venture capital transactions database
├── Dhruval_AIML_Project.ipynb      # Complete AIML Research & Modeling Notebook
├── streamlit_app.py                # Alternate Streamlit presentation dashboard
├── run_server.py                   # One-click launcher for FastAPI full-stack server
├── requirements.txt                # Production dependency specifications
└── README.md                       # Comprehensive documentation
```

---

## 🤖 Machine Learning Pipeline & Methodology

### 1. Target Formulation & Variance Transformation
Venture deal sizes span from \$16,000 to \$3.9 Billion, exhibiting an extreme positive skew ($> 15.0$). To satisfy homoscedasticity assumptions, the target variable is transformed logarithmically:
$$\mathbf{y} = \ln(1 + \text{Amount\_USD})$$
Predictions are mapped back to actual currency via natural exponentiation:
$$\widehat{\text{Amount}} = e^{\widehat{y}} - 1$$

### 2. Feature Architecture
| Feature Name | Type | Processing Pipeline | Description |
| :--- | :--- | :--- | :--- |
| `Industry_Cleaned` | Categorical | `OneHotEncoder(handle_unknown='ignore')` | 9 consolidated tech verticals |
| `City_Cleaned` | Categorical | `OneHotEncoder(handle_unknown='ignore')` | Tier-1 & Tier-2 Indian tech hubs |
| `Investment_Type_Cleaned` | Categorical | `OneHotEncoder(handle_unknown='ignore')` | Seed, Early Stage, Growth, Debt, etc. |
| `Funding_Year` | Numerical | `SimpleImputer(median)` + `StandardScaler` | Temporal funding wave indicator |
| `Investor_Count` | Numerical | `SimpleImputer(median)` + `StandardScaler` | Syndicate size & participation count |

### 3. Model Benchmark & 5-Fold Cross Validation Results
Cross-validated comparison across 6 learning paradigms (evaluated on 5-fold CV & 20% holdout test split):

| Algorithm Architecture | Holdout $R^2$ | RMSE (Log) | MAE (Log) | 5-Fold CV $R^2$ | Architectural Assessment |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Gradient Boosting Regressor** 🏆 | **0.5218** | **1.2389** | **0.9314** | **0.5124** | **Selected Production Model:** Optimal bias-variance balance. |
| **Random Forest Regressor** | 0.4985 | 1.2678 | 0.9541 | 0.4912 | Strong ensemble; slightly higher generalization variance. |
| **Ridge Regression (L2)** | 0.4412 | 1.3382 | 1.0028 | 0.4352 | Underfits non-linear syndication dynamics. |
| **Lasso Regression (L1)** | 0.4285 | 1.3534 | 1.0182 | 0.4218 | Zeroes out subtle geographic indicators. |
| **Decision Tree Regressor** | 0.4231 | 1.3598 | 1.0150 | 0.4180 | Overfits on small feature partitions. |
| **Baseline (Median Dummy)** | -0.0120 | 1.7925 | 1.4420 | -0.0150 | Naive median predictor benchmark. |

### 4. Key Valuation Drivers (Feature Importances)
- **Financing Round Stage:** Accounts for $>55\%$ of model attribution (`Seed / Angel` vs `Growth / Late Stage`).
- **Temporal Factor (`Funding_Year`):** Represents $\approx 7.3\%$ attribution capturing macro liquidity cycles.
- **Investor Syndicate Size (`Investor_Count`):** Demonstrates $\approx 3.0\%$ attribution where larger syndicates correlate with larger ticket sizes.
- **Geographic Primacy:** Bangalore, Mumbai, and Delhi NCR command significant premiums over emerging tech hubs.

---

## ⚡ How to Run the Project

### Option A: Launch Full-Stack Web Application (FastAPI + Modern Web UI)

Run the single-click server launcher from your terminal:
```bash
python run_server.py
```
This automatically initiates the FastAPI backend, loads the machine learning pipeline, and opens your browser at:
- **Web Application:** `http://127.0.0.1:8000`
- **Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`
- **ReDoc Technical Schema:** `http://127.0.0.1:8000/redoc`

---

### Option B: Launch Streamlit Presentation Dashboard

For viva presentations and interactive academic walkthroughs:
```bash
streamlit run streamlit_app.py
```
This launches a 6-tab dashboard with interactive Matplotlib/Seaborn plots, dataframes, and scenario selectors.

---

## 🔌 REST API Documentation

The FastAPI backend exposes the following endpoints:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the interactive full-stack web UI |
| `GET` | `/api/health` | System health check & dataset verification |
| `GET` | `/api/metadata` | Returns valid industries, hubs, investment stages, and macro totals |
| `POST` | `/api/predict` | Computes funding prediction, USD/INR conversion, 90% confidence bounds, and advisory insights |
| `POST` | `/api/what-if` | Runs counterfactual scenario simulation across 9 tech hubs |
| `GET` | `/api/investors` | Returns top active venture capital firms & angel networks with deal counts |
| `GET` | `/api/sectors` | Returns composite Sector Opportunity Scores (0–100) and ticket sizes |
| `GET` | `/api/ecosystem-stats` | Macro yearly deal volumes and city allocation distributions |
| `GET` | `/api/model-info` | Pipeline metadata, hyperparameter specs, benchmark table, and feature importances |

### Sample Prediction Request:
```json
POST /api/predict
Content-Type: application/json

{
  "industry": "FinTech & Payments",
  "city": "Bangalore",
  "investment_type": "Early Stage (Series A/B)",
  "funding_year": 2026,
  "investor_count": 3
}
```

### Sample Prediction Response:
```json
{
  "estimated_amount_usd": 7828461.44,
  "estimated_amount_inr": 653676530.24,
  "formatted_usd": "$7.83 Million",
  "formatted_inr": "₹65.37 Crores",
  "lower_bound_usd": 5479923.01,
  "upper_bound_usd": 10568422.94,
  "formatted_range_usd": "$5.48 Million – $10.57 Million",
  "formatted_range_inr": "₹45.76 Crores – ₹88.25 Crores",
  "valuation_tier": "Early Growth (Series A/B) Bracket",
  "comparable_percentile": 81.6,
  "confidence_level": "90% Empirical Interval",
  "advisory_insights": [
    "Operating from Bangalore grants access to India's dense Tier-1 venture network, commanding a historical valuation premium over secondary hubs.",
    "For Series A/B rounds, institutional investors heavily scrutinize Unit Economics (LTV/CAC > 3x), Monthly Recurring Revenue (MRR) expansion, and retention cohorts.",
    "Optimal syndicate configuration (2-3 institutional participants) offering balanced board representation without dilution fragmentation.",
    "FinTech & Payments historically commands top-quartile median deal sizes due to high customer lifetime values."
  ]
}
```

---

## 🎯 Viva & Presentation Quick Reference

1. **Why was Log Transformation applied on the target?**  
   Venture capital deals have extreme positive skewness (few billion-dollar outliers such as Flipkart/Paytm, with the majority under \$2M). The log transformation $\ln(1 + \text{Amount})$ normalizes residuals and prevents extreme outliers from disproportionately dominating the loss function.

2. **Why Gradient Boosting over Random Forest or Deep Learning?**  
   Tabular venture datasets with categorical and low-cardinality features excel under gradient boosted trees. As proven in the 5-Fold Cross Validation benchmark, Gradient Boosting achieved the highest $R^2$ (0.5218) and lowest RMSE (1.2389), outperforming Random Forest (0.4985) and linear regularized regressors ($0.4285 - 0.4412$).

3. **How does the system prevent data leakage?**  
   The preprocessing transformations (`OneHotEncoder`, `StandardScaler`, `SimpleImputer`) are embedded directly within Scikit-Learn `ColumnTransformer` and chained inside a unified `Pipeline`. Preprocessors are fitted strictly on training folds and re-applied uniformly during inference.
# StartupLens-AI
