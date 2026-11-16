import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "startup_funding_predictor.joblib"
DATA_PATH = BASE_DIR / "startup_funding.csv"
FRONTEND_DIR = BASE_DIR / "frontend"

# Currency conversion rate (USD to INR estimate)
USD_TO_INR_RATE = 83.50

# Supported categorical options from ML training set
INDUSTRIES = [
    "Technology & Enterprise SaaS",
    "FinTech & Payments",
    "E-Commerce & Retail",
    "HealthTech & Wellness",
    "EdTech",
    "Consumer Internet & Media",
    "Logistics & Supply Chain",
    "FoodTech & Hospitality",
    "Other / Emerging"
]

CITIES = [
    "Bangalore",
    "Delhi NCR",
    "Mumbai",
    "Pune",
    "Hyderabad",
    "Chennai",
    "Ahmedabad",
    "Jaipur",
    "Kolkata",
    "Other"
]

INVESTMENT_TYPES = [
    "Seed / Angel",
    "Early Stage (Series A/B)",
    "Growth / Late Stage (Series C+)",
    "Venture Debt",
    "Crowdfunding",
    "Other"
]

# Benchmark Results from Notebook Experimentation (5-Fold Cross Validation + Holdout Test)
MODEL_BENCHMARKS = [
    {
        "algorithm": "Gradient Boosting Regressor",
        "is_best": True,
        "cv_r2": 0.5124,
        "cv_rmse": 1.2582,
        "cv_mae": 0.9421,
        "test_r2": 0.5218,
        "test_rmse": 1.2389,
        "test_mae": 0.9314,
        "description": "Selected production model with optimal variance control and lowest generalization error."
    },
    {
        "algorithm": "Random Forest Regressor",
        "is_best": False,
        "cv_r2": 0.4912,
        "cv_rmse": 1.2854,
        "cv_mae": 0.9632,
        "test_r2": 0.4985,
        "test_rmse": 1.2678,
        "test_mae": 0.9541,
        "description": "High non-linear capacity; slightly higher generalization variance than Gradient Boosting."
    },
    {
        "algorithm": "Decision Tree Regressor",
        "is_best": False,
        "cv_r2": 0.4180,
        "cv_rmse": 1.3742,
        "cv_mae": 1.0210,
        "test_r2": 0.4231,
        "test_rmse": 1.3598,
        "test_mae": 1.0150,
        "description": "Fast tree partitioner, prone to high-variance overfitting on small feature subsets."
    },
    {
        "algorithm": "Ridge Regression",
        "is_best": False,
        "cv_r2": 0.4352,
        "cv_rmse": 1.3541,
        "cv_mae": 1.0125,
        "test_r2": 0.4412,
        "test_rmse": 1.3382,
        "test_mae": 1.0028,
        "description": "Linear L2 regularization, underfits intricate non-linear market dynamics."
    },
    {
        "algorithm": "Lasso Regression",
        "is_best": False,
        "cv_r2": 0.4218,
        "cv_rmse": 1.3702,
        "cv_mae": 1.0289,
        "test_r2": 0.4285,
        "test_rmse": 1.3534,
        "test_mae": 1.0182,
        "description": "Linear L1 sparsity penalty, shrinks several valuable city indicators to zero."
    },
    {
        "algorithm": "Baseline (Median Dummy)",
        "is_best": False,
        "cv_r2": -0.0150,
        "cv_rmse": 1.8021,
        "cv_mae": 1.4512,
        "test_r2": -0.0120,
        "test_rmse": 1.7925,
        "test_mae": 1.4420,
        "description": "Naive benchmark predicting median log-funding amount."
    }
]

BEST_HYPERPARAMETERS = {
    "model__n_estimators": 150,
    "model__learning_rate": 0.08,
    "model__max_depth": 4,
    "random_state": 42
}
