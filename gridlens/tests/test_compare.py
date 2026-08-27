from __future__ import annotations

import pytest

from gridlens.domain.models import ScenarioRequest


@pytest.mark.asyncio
async def test_compare_returns_delta(async_client) -> None:
    payload = {
        "base": ScenarioRequest(scenario_id="base").model_dump(),
        "compare": ScenarioRequest(scenario_id="compare", battery_capacity_kwh=150.0).model_dump(),
    }
    response = await async_client.post("/api/scenarios/compare", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data["delta_cost_usd"], float)


@pytest.mark.asyncio
async def test_compare_zero_delta(async_client) -> None:
    request = ScenarioRequest(scenario_id="same").model_dump()
    response = await async_client.post("/api/scenarios/compare", json={"base": request, "compare": request})
    data = response.json()

    assert response.status_code == 200
    assert data["delta_cost_usd"] == pytest.approx(0.0)
    assert data["delta_emissions_kg_co2"] == pytest.approx(0.0)
    assert data["delta_solar_fraction"] == pytest.approx(0.0)
    assert data["delta_self_sufficiency"] == pytest.approx(0.0)
    assert data["delta_grid_import_kwh"] == pytest.approx(0.0)
    assert data["delta_curtailment_kwh"] == pytest.approx(0.0)


@pytest.mark.asyncio
async def test_forecast_api(async_client) -> None:
    response = await async_client.get("/api/forecast", params={"scenario_id": "default", "horizon_hours": 48})
    assert response.status_code == 200
