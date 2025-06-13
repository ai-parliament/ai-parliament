"""
API routes for the backend server.
"""

from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from .ai_service import AIService

# Initialize router
router = APIRouter(prefix="/api")

# Initialize AI service
ai_service = AIService()

# Health check endpoint
@router.get("/health")
def health_check():
    """Health check endpoint for Docker healthcheck"""
    return {"status": "healthy"}


# Define request and response models
class SimulationCreateRequest(BaseModel):
    party_names: List[str]
    politicians_per_party: Dict[str, List[Dict[str, str]]]


class GenerateLegislationRequest(BaseModel):
    topic: str


class LegislationRequest(BaseModel):
    legislation_text: str


# API routes
@router.post("/create_simulation")
def create_simulation(request: SimulationCreateRequest):
    """
    Create a new simulation with the specified parties and politicians.
    """
    try:
        result = ai_service.create_simulation(request.party_names, request.politicians_per_party)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate_legislation")
def generate_legislation(request: GenerateLegislationRequest):
    """
    Generate legislation on the specified topic.
    """
    try:
        legislation_text = ai_service.generate_legislation(request.topic)
        return {"legislation_text": legislation_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run_intra_party_deliberation")
def run_intra_party_deliberation(request: LegislationRequest):
    """
    Run the intra-party deliberation phase.
    """
    try:
        result = ai_service.run_intra_party_deliberation(request.legislation_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run_inter_party_debate")
def run_inter_party_debate(request: LegislationRequest):
    """
    Run the inter-party debate phase.
    """
    try:
        result = ai_service.run_inter_party_debate(request.legislation_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run_voting")
def run_voting(request: LegislationRequest):
    """
    Run the voting phase.
    """
    try:
        result = ai_service.run_voting(request.legislation_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_simulation_summary")
def get_simulation_summary():
    """
    Get a summary of the simulation results.
    """
    try:
        result = ai_service.get_simulation_summary()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# backend/src/api/routes.py
@router.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    from ai.src.agents.cache_manager import cache_manager
    return cache_manager.get_cache_stats()

@router.post("/api/cache/clear")
async def clear_cache(max_age_days: int = 30):
    """Clear old cache entries"""
    from ai.src.agents.cache_manager import cache_manager
    cleared = cache_manager.clear_old_cache(max_age_days)
    return {"cleared": cleared}

@router.post("/api/cache/warm")
async def warm_cache(party_names: List[str] = None):
    """Warm cache for specific parties"""
    # Implementation of cache warming
    pass


def create_app():
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(title="AI Parliament Backend API")
    app.include_router(router)
    return app