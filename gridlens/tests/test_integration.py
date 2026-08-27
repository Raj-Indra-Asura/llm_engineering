from __future__ import annotations

import pytest

from gridlens.domain.engine import run_scenario
from gridlens.domain.models import ScenarioRequest


@pytest.mark.asyncio
async def test_health_endpoint(async_client) -> None:
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_run_scenario_endpoint(async_client) -> None:
    response = await async_client.post("/api/scenarios/run", json=ScenarioRequest().model_dump())
    assert response.status_code == 200
    assert response.json()["scenario_id"] == "default"


@pytest.mark.asyncio
async def test_compare_endpoint(async_client) -> None:
    payload = {
        "base": ScenarioRequest(scenario_id="base").model_dump(),
        "compare": ScenarioRequest(scenario_id="compare", solar_capacity_kw=300.0).model_dump(),
    }
    response = await async_client.post("/api/scenarios/compare", json=payload)
    assert response.status_code == 200
    assert "delta_cost_usd" in response.json()


@pytest.mark.asyncio
async def test_forecast_endpoint(async_client) -> None:
    response = await async_client.get("/api/forecast", params={"scenario_id": "default", "horizon_hours": 24})
    assert response.status_code == 200
    assert response.json()["method"] == "seasonal_naive"


@pytest.mark.asyncio
async def test_explain_endpoint_offline(async_client) -> None:
    result = run_scenario(ScenarioRequest())
    response = await async_client.post(
        "/api/explain",
        json={"scenario_id": result.scenario_id, "question": "What is solar fraction?", "result": result.model_dump()},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["evidence_found"] is True
    assert len(data["sources"]) >= 1


@pytest.mark.asyncio
async def test_explain_no_evidence(async_client) -> None:
    result = run_scenario(ScenarioRequest())
    response = await async_client.post(
        "/api/explain",
        json={
            "scenario_id": result.scenario_id,
            "question": "xyzzy quux blorb snth",
            "result": result.model_dump(),
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data["evidence_found"] is False
