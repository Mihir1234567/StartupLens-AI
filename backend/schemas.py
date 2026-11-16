from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class PredictionRequest(BaseModel):
    industry: str = Field(..., example="FinTech & Payments", description="Target industry vertical")
    city: str = Field(..., example="Bangalore", description="Primary startup operating hub")
    investment_type: str = Field(..., example="Early Stage (Series A/B)", description="Funding round stage")
    funding_year: int = Field(2026, ge=2015, le=2030, description="Funding year")
    investor_count: int = Field(2, ge=1, le=20, description="Number of participating investors/syndicate size")

class PredictionResponse(BaseModel):
    estimated_amount_usd: float
    estimated_amount_inr: float
    formatted_usd: str
    formatted_inr: str
    lower_bound_usd: float
    upper_bound_usd: float
    formatted_range_usd: str
    formatted_range_inr: str
    valuation_tier: str
    comparable_percentile: float
    confidence_level: str
    advisory_insights: List[str]

class WhatIfRequest(BaseModel):
    industry: str = Field(..., example="Technology & Enterprise SaaS")
    investment_type: str = Field(..., example="Early Stage (Series A/B)")
    funding_year: int = Field(2026, ge=2015, le=2030)
    investor_count: int = Field(2, ge=1, le=20)
    candidate_cities: Optional[List[str]] = None

class WhatIfCityResult(BaseModel):
    city: str
    estimated_amount_usd: float
    formatted_usd: str
    formatted_inr: str
    variance_pct: float
    is_highest: bool

class WhatIfResponse(BaseModel):
    base_config: Dict[str, Any]
    results: List[WhatIfCityResult]
    top_city: str
    max_funding_usd: float

class MetadataResponse(BaseModel):
    industries: List[str]
    cities: List[str]
    investment_types: List[str]
    total_deals: int
    total_capital_deployed_usd: float
    total_capital_formatted_usd: str
    total_capital_formatted_inr: str

class InvestorStat(BaseModel):
    name: str
    deal_count: int

class SectorOpportunityItem(BaseModel):
    industry: str
    opportunity_score: float
    total_funding_usd: float
    formatted_total_usd: str
    funding_rounds: int
    median_funding_usd: float
    formatted_median_usd: str
    active_cities_count: int

class ModelInfoResponse(BaseModel):
    pipeline_architecture: str
    best_algorithm: str
    hyperparameters: Dict[str, Any]
    metrics: Dict[str, float]
    benchmarks: List[Dict[str, Any]]
    feature_importances: List[Dict[str, Any]]
