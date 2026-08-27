from __future__ import annotations

from fastapi import APIRouter

from gridlens.domain.engine import run_scenario
from gridlens.domain.models import ScenarioRequest, ScenarioResult

router = APIRouter()


@router.post("/scenarios/run", response_model=ScenarioResult)
def run_scenario_endpoint(request: ScenarioRequest) -> ScenarioResult:
    return run_scenario(request)
