from __future__ import annotations

from fastapi import APIRouter, Query

from gridlens.domain.engine import run_scenario
from gridlens.domain.forecast import run_forecast
from gridlens.domain.models import (
    ForecastResult,
    ScenarioComparison,
    ScenarioComparisonRequest,
    ScenarioRequest,
)

router = APIRouter()


def _build_summary(comparison: ScenarioComparison) -> str:
    direction = "reduced" if comparison.delta_cost_usd <= 0 else "increased"
    emissions_direction = "reduced" if comparison.delta_emissions_kg_co2 <= 0 else "increased"
    return (
        f"Scenario '{comparison.compare_scenario_id}' {direction} cost by "
        f"{abs(comparison.delta_cost_usd):.2f} USD and {emissions_direction} emissions by "
        f"{abs(comparison.delta_emissions_kg_co2):.2f} kgCO2 versus '{comparison.base_scenario_id}'."
    )


@router.post("/scenarios/compare", response_model=ScenarioComparison)
def compare_scenarios(request: ScenarioComparisonRequest) -> ScenarioComparison:
    base_result = run_scenario(request.base)
    compare_result = run_scenario(request.compare)

    comparison = ScenarioComparison(
        base_scenario_id=base_result.scenario_id,
        compare_scenario_id=compare_result.scenario_id,
        delta_cost_usd=compare_result.total_cost_usd - base_result.total_cost_usd,
        delta_emissions_kg_co2=compare_result.total_emissions_kg_co2 - base_result.total_emissions_kg_co2,
        delta_solar_fraction=compare_result.solar_fraction - base_result.solar_fraction,
        delta_self_sufficiency=compare_result.self_sufficiency - base_result.self_sufficiency,
        delta_grid_import_kwh=compare_result.total_grid_import_kwh - base_result.total_grid_import_kwh,
        delta_curtailment_kwh=compare_result.total_curtailment_kwh - base_result.total_curtailment_kwh,
        summary="",
    )
    return comparison.model_copy(update={"summary": _build_summary(comparison)})


@router.get("/forecast", response_model=ForecastResult)
def forecast_endpoint(
    scenario_id: str = Query(default="default"),
    horizon_hours: int = Query(default=48, ge=1, le=168),
) -> ForecastResult:
    request = ScenarioRequest(scenario_id=scenario_id, horizon_hours=horizon_hours)
    return run_forecast(request)
