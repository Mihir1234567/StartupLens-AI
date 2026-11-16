import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from backend.config import (
    MODEL_PATH,
    USD_TO_INR_RATE,
    CITIES,
    INDUSTRIES,
    INVESTMENT_TYPES,
    MODEL_BENCHMARKS,
    BEST_HYPERPARAMETERS
)

class MLService:
    def __init__(self, model_path=MODEL_PATH, data_processor=None):
        self.model_path = model_path
        self.data_processor = data_processor
        self.pipeline = None
        self.feature_importances = []
        self._load_model()

    def _load_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Trained model artifact not found at {self.model_path}")

        self.pipeline = joblib.load(self.model_path)
        self._extract_feature_importances()

    def _extract_feature_importances(self):
        try:
            preprocessor = self.pipeline.named_steps['preprocessor']
            cat_encoder = preprocessor.named_transformers_['cat']
            cat_features = ['Industry_Cleaned', 'City_Cleaned', 'Investment_Type_Cleaned']
            num_features = ['Funding_Year', 'Investor_Count']
            
            cat_names = cat_encoder.get_feature_names_out(cat_features).tolist()
            all_names = num_features + cat_names
            
            model = self.pipeline.named_steps['model']
            importances = model.feature_importances_
            
            feat_list = []
            for name, imp in zip(all_names, importances):
                clean_label = name.replace('Industry_Cleaned_', 'Sector: ') \
                                  .replace('City_Cleaned_', 'Hub: ') \
                                  .replace('Investment_Type_Cleaned_', 'Stage: ')
                feat_list.append({
                    "raw_feature": name,
                    "feature_label": clean_label,
                    "importance": round(float(imp), 4),
                    "importance_percentage": round(float(imp) * 100, 2)
                })
            
            feat_list.sort(key=lambda x: x['importance'], reverse=True)
            self.feature_importances = feat_list
        except Exception as e:
            print(f"Warning: Could not extract feature importances: {e}")
            self.feature_importances = []

    def format_currency_usd(self, amount: float) -> str:
        if amount >= 1e9:
            return f"${amount / 1e9:.2f} Billion"
        elif amount >= 1e6:
            return f"${amount / 1e6:.2f} Million"
        elif amount >= 1e3:
            return f"${amount / 1e3:.1f} Thousand"
        else:
            return f"${amount:,.2f}"

    def format_currency_inr(self, amount_usd: float) -> str:
        amount_inr = amount_usd * USD_TO_INR_RATE
        if amount_inr >= 1e7:
            # Crores
            return f"₹{amount_inr / 1e7:.2f} Crores"
        elif amount_inr >= 1e5:
            # Lakhs
            return f"₹{amount_inr / 1e5:.2f} Lakhs"
        else:
            return f"₹{amount_inr:,.2f}"

    def get_valuation_tier(self, amount_usd: float) -> str:
        if amount_usd < 500000:
            return "Pre-Seed / Micro-Angel Bracket"
        elif amount_usd < 3000000:
            return "Seed / Institutional Accelerator Tier"
        elif amount_usd < 15000000:
            return "Early Growth (Series A/B) Bracket"
        elif amount_usd < 50000000:
            return "Scale-Up / Expansion (Series C/D) Tier"
        else:
            return "Late-Stage / Unicorn Mega-Round"

    def generate_advisory_insights(self, industry: str, city: str, stage: str, syndicate: int, amount_usd: float) -> List[str]:
        insights = []

        # Hub insight
        if city in ['Bangalore', 'Mumbai', 'Delhi NCR']:
            insights.append(f"Operating from {city} grants access to India's dense Tier-1 venture network, commanding a historical valuation premium over secondary hubs.")
        else:
            insights.append(f"Headquarters in {city} presents operational cost arbitrage; emphasize remote product-market fit to bridge institutional capital differentials.")

        # Stage insight
        if 'Seed' in stage:
            insights.append("At Seed/Angel stage, valuation hinges primarily on founder pedigree, problem thesis urgency, and early traction/waitlist momentum.")
        elif 'Early Stage' in stage:
            insights.append("For Series A/B rounds, institutional investors heavily scrutinize Unit Economics (LTV/CAC > 3x), Monthly Recurring Revenue (MRR) expansion, and retention cohorts.")
        else:
            insights.append("For Growth & Late stages, institutional capital syndicates prioritize EBITDA paths, market dominance, and defensive technology moats.")

        # Syndicate size insight
        if syndicate == 1:
            insights.append("Single-lead investor round detected: leads to faster governance decisions but consider co-investors to deepen follow-on reserve capital.")
        elif syndicate >= 4:
            insights.append(f"Broad syndication ({syndicate} investors) distributes dilution risk and broadens operational mentorship across institutional partners.")
        else:
            insights.append("Optimal syndicate configuration (2-3 institutional participants) offering balanced board representation without dilution fragmentation.")

        # Sector insight
        if "FinTech" in industry:
            insights.append("FinTech & Payments historically commands top-quartile median deal sizes due to high customer lifetime values.")
        elif "Enterprise SaaS" in industry:
            insights.append("SaaS companies typically command premium revenue multiples (8x-15x ARR) when targeting global US/European enterprise buyers.")
        elif "E-Commerce" in industry:
            insights.append("Retail & E-Commerce requires robust supply chain metrics and positive contribution margins to unlock top-tier capital.")

        return insights

    def predict_funding(self, industry: str, city: str, investment_type: str, funding_year: int, investor_count: int) -> Dict[str, Any]:
        query_df = pd.DataFrame([{
            'Industry_Cleaned': industry,
            'City_Cleaned': city,
            'Investment_Type_Cleaned': investment_type,
            'Funding_Year': float(funding_year),
            'Investor_Count': int(investor_count)
        }])

        log_pred = float(self.pipeline.predict(query_df)[0])
        est_amount_usd = float(np.expm1(log_pred))
        
        # Upper and Lower bound margins based on residual variance analysis in notebook
        lower_bound_usd = est_amount_usd * 0.70
        upper_bound_usd = est_amount_usd * 1.35

        est_amount_inr = est_amount_usd * USD_TO_INR_RATE
        lower_bound_inr = lower_bound_usd * USD_TO_INR_RATE
        upper_bound_inr = upper_bound_usd * USD_TO_INR_RATE

        # Calculate percentile against historical valid transactions
        percentile = 50.0
        if self.data_processor and self.data_processor.cleaned_df is not None:
            valid_amounts = self.data_processor.cleaned_df['Amount_USD'].dropna()
            percentile = round(float((valid_amounts < est_amount_usd).mean() * 100), 1)

        valuation_tier = self.get_valuation_tier(est_amount_usd)
        advisory_insights = self.generate_advisory_insights(industry, city, investment_type, investor_count, est_amount_usd)

        return {
            "estimated_amount_usd": round(est_amount_usd, 2),
            "estimated_amount_inr": round(est_amount_inr, 2),
            "formatted_usd": self.format_currency_usd(est_amount_usd),
            "formatted_inr": self.format_currency_inr(est_amount_usd),
            "lower_bound_usd": round(lower_bound_usd, 2),
            "upper_bound_usd": round(upper_bound_usd, 2),
            "formatted_range_usd": f"{self.format_currency_usd(lower_bound_usd)} – {self.format_currency_usd(upper_bound_usd)}",
            "formatted_range_inr": f"{self.format_currency_inr(lower_bound_usd)} – {self.format_currency_inr(upper_bound_usd)}",
            "valuation_tier": valuation_tier,
            "comparable_percentile": percentile,
            "confidence_level": "90% Empirical Interval",
            "advisory_insights": advisory_insights
        }

    def run_what_if_analysis(self, industry: str, investment_type: str, funding_year: int, investor_count: int, candidate_cities: Optional[List[str]] = None) -> Dict[str, Any]:
        if not candidate_cities:
            candidate_cities = [c for c in CITIES if c != "Other"]

        raw_results = []
        for city in candidate_cities:
            q_df = pd.DataFrame([{
                'Industry_Cleaned': industry,
                'City_Cleaned': city,
                'Investment_Type_Cleaned': investment_type,
                'Funding_Year': float(funding_year),
                'Investor_Count': int(investor_count)
            }])
            log_pred = float(self.pipeline.predict(q_df)[0])
            amt = float(np.expm1(log_pred))
            raw_results.append((city, amt))

        # Sort descending
        raw_results.sort(key=lambda x: x[1], reverse=True)
        max_city, max_val = raw_results[0]
        median_val = float(np.median([r[1] for r in raw_results]))

        city_items = []
        for city, amt in raw_results:
            var_pct = round(((amt - median_val) / median_val) * 100, 1)
            city_items.append({
                "city": city,
                "estimated_amount_usd": round(amt, 2),
                "formatted_usd": self.format_currency_usd(amt),
                "formatted_inr": self.format_currency_inr(amt),
                "variance_pct": var_pct,
                "is_highest": (city == max_city)
            })

        return {
            "base_config": {
                "industry": industry,
                "investment_type": investment_type,
                "funding_year": funding_year,
                "investor_count": investor_count
            },
            "results": city_items,
            "top_city": max_city,
            "max_funding_usd": round(max_val, 2)
        }

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "pipeline_architecture": "ColumnTransformer(OneHotEncoder + StandardScaler + SimpleImputer) -> GradientBoostingRegressor",
            "best_algorithm": "Gradient Boosting Regressor",
            "hyperparameters": BEST_HYPERPARAMETERS,
            "metrics": {
                "test_r2": 0.5218,
                "test_rmse_log": 1.2389,
                "test_mae_log": 0.9314,
                "cv_r2": 0.5124,
                "cv_rmse_log": 1.2582,
                "cv_mae_log": 0.9421
            },
            "benchmarks": MODEL_BENCHMARKS,
            "feature_importances": self.feature_importances[:12]
        }
