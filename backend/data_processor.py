import re
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from backend.config import DATA_PATH, USD_TO_INR_RATE

class DataProcessor:
    def __init__(self, data_path=DATA_PATH):
        self.data_path = data_path
        self.df_raw = None
        self.cleaned_df = None
        self._load_and_clean()

    def _load_and_clean(self):
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Dataset not found at {self.data_path}")

        self.df_raw = pd.read_csv(self.data_path)
        df = self.df_raw.copy()

        # 1. Clean Amount in USD
        def clean_amount(val):
            if pd.isna(val): return np.nan
            val = str(val).strip().replace(',', '')
            if re.search(r'(?i)undisclosed|unknown|n/a|\+|unknown', val): return np.nan
            val = re.sub(r'[^0-9.]', '', val)
            try:
                f = float(val)
                return f if f > 0 else np.nan
            except:
                return np.nan

        df['Amount_USD'] = df['Amount in USD'].apply(clean_amount)

        # 2. Clean Dates & Extract Temporal Attributes
        def clean_date(val):
            if pd.isna(val): return np.nan
            val = str(val).strip().replace('.', '/').replace('//', '/')
            match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', val)
            if match:
                return f"{match.group(1).zfill(2)}/{match.group(2).zfill(2)}/{match.group(3)}"
            return np.nan

        df['Clean_Date'] = df['Date dd/mm/yyyy'].apply(clean_date)
        df['Clean_Date'] = pd.to_datetime(df['Clean_Date'], format='%d/%m/%Y', errors='coerce')
        df['Funding_Year'] = df['Clean_Date'].dt.year
        df['Funding_Month'] = df['Clean_Date'].dt.month
        df['Funding_Quarter'] = df['Clean_Date'].dt.quarter

        # 3. Clean and Consolidate Cities
        def clean_city(val):
            if pd.isna(val): return 'Other'
            val = str(val).strip().split('/')[0].strip()
            val = val.replace('\\xc2\\xa0', '').replace('&nbsp;', '')
            mapping = {
                'Bengaluru': 'Bangalore', 'Gurugram': 'Delhi NCR', 'New Delhi': 'Delhi NCR',
                'Noida': 'Delhi NCR', 'Delhi': 'Delhi NCR', 'Gurgaon': 'Delhi NCR'
            }
            cleaned = mapping.get(val, val)
            top_cities = ['Bangalore', 'Delhi NCR', 'Mumbai', 'Pune', 'Hyderabad', 'Chennai', 'Ahmedabad', 'Jaipur', 'Kolkata']
            return cleaned if cleaned in top_cities else 'Other'

        df['City_Cleaned'] = df['City  Location'].apply(clean_city)

        # 4. Clean Investment Types
        def clean_investment_type(val):
            if pd.isna(val): return 'Other'
            v = str(val).strip().lower()
            if 'seed' in v or 'pre-seed' in v or 'angel' in v:
                return 'Seed / Angel'
            elif 'series a' in v or 'series b' in v or 'pre-series a' in v:
                return 'Early Stage (Series A/B)'
            elif any(s in v for s in ['series c', 'series d', 'series e', 'series f', 'series g', 'series h', 'private equity']):
                return 'Growth / Late Stage (Series C+)'
            elif 'debt' in v:
                return 'Venture Debt'
            elif 'crowd' in v:
                return 'Crowdfunding'
            return 'Other'

        df['Investment_Type_Cleaned'] = df['InvestmentnType'].apply(clean_investment_type)

        # 5. Clean Industry Verticals
        def clean_industry(val):
            if pd.isna(val): return 'Other / Emerging'
            v = str(val).strip().lower()
            if any(k in v for k in ['ecommerce', 'e-commerce', 'e - commerce', 'online marketplace', 'retail']):
                return 'E-Commerce & Retail'
            elif any(k in v for k in ['fintech', 'finance', 'financial', 'banking', 'payment', 'wealth']):
                return 'FinTech & Payments'
            elif any(k in v for k in ['edtech', 'education', 'e-learning', 'skill']):
                return 'EdTech'
            elif any(k in v for k in ['health', 'healthcare', 'medical', 'pharma', 'fitness']):
                return 'HealthTech & Wellness'
            elif any(k in v for k in ['logistics', 'supply chain', 'transport', 'courier', 'delivery']):
                return 'Logistics & Supply Chain'
            elif any(k in v for k in ['food', 'beverage', 'restaurant', 'dining', 'culinary']):
                return 'FoodTech & Hospitality'
            elif any(k in v for k in ['consumer internet', 'social', 'media', 'entertainment', 'gaming']):
                return 'Consumer Internet & Media'
            elif any(k in v for k in ['technology', 'tech', 'software', 'saas', 'enterprise', 'it', 'cloud', 'ai', 'iot', 'analytics']):
                return 'Technology & Enterprise SaaS'
            return 'Other / Emerging'

        df['Industry_Cleaned'] = df['Industry Vertical'].apply(clean_industry)

        # 6. Extract Investor Count
        def get_investor_count(val):
            if pd.isna(val): return 1
            names = [n.strip() for n in str(val).split(',') if n.strip() and n.strip().lower() not in ['', 'undisclosed', 'undisclosed investors', 'undisclosed investor']]
            return max(1, len(names))

        df['Investor_Count'] = df['Investors Name'].apply(get_investor_count)
        self.cleaned_df = df

    def get_summary_metadata(self) -> Dict[str, Any]:
        total_deals = len(self.cleaned_df)
        total_capital = float(self.cleaned_df['Amount_USD'].dropna().sum())
        
        # Formatted strings
        if total_capital >= 1e9:
            fmt_usd = f"${total_capital / 1e9:.2f} Billion"
        else:
            fmt_usd = f"${total_capital / 1e6:.2f} Million"

        total_capital_inr = total_capital * USD_TO_INR_RATE
        # Convert INR to Crores (1 Crore = 10 Million INR)
        fmt_inr = f"₹{total_capital_inr / 1e7:,.2f} Cr"

        return {
            "total_deals": total_deals,
            "total_capital_deployed_usd": total_capital,
            "total_capital_formatted_usd": fmt_usd,
            "total_capital_formatted_inr": fmt_inr
        }

    def get_investor_analytics(self, top_n: int = 15) -> List[Dict[str, Any]]:
        investor_series = self.cleaned_df['Investors Name'].dropna().str.split(',').explode().str.strip()
        invalid_names = ['', 'undisclosed', 'undisclosed investors', 'undisclosed investor', 'undisclosed series a investor']
        investor_series = investor_series[~investor_series.str.lower().isin(invalid_names)]
        top_investors = investor_series.value_counts().head(top_n)
        
        results = []
        for name, count in top_investors.items():
            results.append({"name": str(name), "deal_count": int(count)})
        return results

    def compute_sector_scores(self) -> List[Dict[str, Any]]:
        sector_stats = self.cleaned_df.groupby('Industry_Cleaned').agg(
            total_funding=('Amount_USD', 'sum'),
            funding_rounds=('Amount_USD', 'count'),
            median_funding=('Amount_USD', 'median'),
            active_cities=('City_Cleaned', 'nunique')
        ).reset_index().fillna(0)

        max_funding = sector_stats['total_funding'].max()
        max_rounds = sector_stats['funding_rounds'].max()
        max_cities = max(1, sector_stats['active_cities'].max())

        sector_stats['Opportunity_Score'] = (
            (sector_stats['total_funding'] / max_funding * 40) +
            (sector_stats['funding_rounds'] / max_rounds * 40) +
            (sector_stats['active_cities'] / max_cities * 20)
        ).round(2)

        sorted_df = sector_stats.sort_values(by='Opportunity_Score', ascending=False)
        
        output = []
        for _, row in sorted_df.iterrows():
            tot = float(row['total_funding'])
            med = float(row['median_funding'])
            output.append({
                "industry": str(row['Industry_Cleaned']),
                "opportunity_score": float(row['Opportunity_Score']),
                "total_funding_usd": tot,
                "formatted_total_usd": f"${tot/1e9:.2f}B" if tot >= 1e9 else f"${tot/1e6:.1f}M",
                "funding_rounds": int(row['funding_rounds']),
                "median_funding_usd": med,
                "formatted_median_usd": f"${med/1e6:.2f}M" if med >= 1e6 else f"${med/1e3:.0f}K",
                "active_cities_count": int(row['active_cities'])
            })
        return output

    def get_ecosystem_overview(self) -> Dict[str, Any]:
        # Funding by Year
        year_df = self.cleaned_df.dropna(subset=['Funding_Year']).copy()
        year_stats = year_df.groupby('Funding_Year').agg(
            deal_count=('Amount_USD', 'count'),
            total_funding=('Amount_USD', 'sum')
        ).reset_index()
        year_stats['Funding_Year'] = year_stats['Funding_Year'].astype(int)
        
        years_data = []
        for _, row in year_stats.iterrows():
            years_data.append({
                "year": int(row['Funding_Year']),
                "deal_count": int(row['deal_count']),
                "total_funding_m": round(float(row['total_funding']) / 1e6, 2)
            })

        # Top Cities by volume & capital
        city_stats = self.cleaned_df.groupby('City_Cleaned').agg(
            deal_count=('Amount_USD', 'count'),
            total_funding=('Amount_USD', 'sum')
        ).sort_values(by='total_funding', ascending=False).reset_index()

        cities_data = []
        for _, row in city_stats.iterrows():
            cities_data.append({
                "city": str(row['City_Cleaned']),
                "deal_count": int(row['deal_count']),
                "total_funding_m": round(float(row['total_funding']) / 1e6, 2)
            })

        return {
            "yearly_trends": years_data,
            "city_distribution": cities_data
        }
