import os
import starlette.routing

# Compatibility patch for Starlette >= 1.0 where on_startup/on_shutdown were replaced by lifespan
_orig_router_init = starlette.routing.Router.__init__
def _patched_router_init(self, *args, **kwargs):
    kwargs.pop('on_startup', None)
    kwargs.pop('on_shutdown', None)
    return _orig_router_init(self, *args, **kwargs)
starlette.routing.Router.__init__ = _patched_router_init

from fastapi import FastAPI, HTTPException, Request

# Compatibility patch: Starlette 1.0+ build_middleware_stack expects max_body_size on the application instance
FastAPI.max_body_size = None
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from typing import Optional, List

from backend.config import (
    INDUSTRIES,
    CITIES,
    INVESTMENT_TYPES,
    FRONTEND_DIR
)
from backend.schemas import (
    PredictionRequest,
    PredictionResponse,
    WhatIfRequest,
    WhatIfResponse,
    MetadataResponse,
    InvestorStat,
    SectorOpportunityItem,
    ModelInfoResponse
)
from backend.data_processor import DataProcessor
from backend.ml_service import MLService

# Initialize FastAPI App
app = FastAPI(
    title="StartupLens AI API",
    description="Venture Valuation, Funding Dynamics, and Investor Intelligence Engine for Indian Startup Ecosystem",
    version="1.0.0"
)

# Enable CORS for external frontend or development setups
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Data Processor and ML Service
print("Initializing DataProcessor and loading dataset...")
data_processor = DataProcessor()
print("Initializing MLService and loading trained pipeline...")
ml_service = MLService(data_processor=data_processor)

# Mount Static Files
static_dir = FRONTEND_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = FRONTEND_DIR / "templates" / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>StartupLens AI Backend Running. (Frontend index.html not found)</h1>")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": ml_service.pipeline is not None,
        "dataset_records": len(data_processor.cleaned_df) if data_processor.cleaned_df is not None else 0
    }

@app.get("/api/metadata", response_model=MetadataResponse)
async def get_metadata():
    summary = data_processor.get_summary_metadata()
    return MetadataResponse(
        industries=INDUSTRIES,
        cities=CITIES,
        investment_types=INVESTMENT_TYPES,
        total_deals=summary["total_deals"],
        total_capital_deployed_usd=summary["total_capital_deployed_usd"],
        total_capital_formatted_usd=summary["total_capital_formatted_usd"],
        total_capital_formatted_inr=summary["total_capital_formatted_inr"]
    )

@app.post("/api/predict", response_model=PredictionResponse)
async def predict_funding(request: PredictionRequest):
    try:
        result = ml_service.predict_funding(
            industry=request.industry,
            city=request.city,
            investment_type=request.investment_type,
            funding_year=request.funding_year,
            investor_count=request.investor_count
        )
        return PredictionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/api/what-if", response_model=WhatIfResponse)
async def run_what_if(request: WhatIfRequest):
    try:
        result = ml_service.run_what_if_analysis(
            industry=request.industry,
            investment_type=request.investment_type,
            funding_year=request.funding_year,
            investor_count=request.investor_count,
            candidate_cities=request.candidate_cities
        )
        return WhatIfResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"What-If simulation error: {str(e)}")

@app.get("/api/investors", response_model=List[InvestorStat])
async def get_investors(top_n: int = 15):
    try:
        data = data_processor.get_investor_analytics(top_n=top_n)
        return [InvestorStat(**item) for item in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Investor analytics error: {str(e)}")

@app.get("/api/sectors", response_model=List[SectorOpportunityItem])
async def get_sectors():
    try:
        data = data_processor.compute_sector_scores()
        return [SectorOpportunityItem(**item) for item in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sector scoring error: {str(e)}")

@app.get("/api/ecosystem-stats")
async def get_ecosystem_stats():
    try:
        return data_processor.get_ecosystem_overview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ecosystem analytics error: {str(e)}")

@app.get("/api/model-info", response_model=ModelInfoResponse)
async def get_model_info():
    try:
        info = ml_service.get_model_info()
        return ModelInfoResponse(**info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model diagnostics error: {str(e)}")
