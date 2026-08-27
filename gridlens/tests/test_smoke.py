from __future__ import annotations

import os

import pytest

from gridlens.domain.engine import run_scenario
from gridlens.domain.models import ScenarioRequest


@pytest.mark.asyncio
async def test_smoke_health(async_client) -> None:
    response = await async_client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_smoke_run_scenario(async_client) -> None:
    response = await async_client.post("/api/scenarios/run", json=ScenarioRequest().model_dump())
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_smoke_compare(async_client) -> None:
    payload = {
        "base": ScenarioRequest(scenario_id="base").model_dump(),
        "compare": ScenarioRequest(scenario_id="compare", battery_capacity_kwh=125.0).model_dump(),
    }
    response = await async_client.post("/api/scenarios/compare", json=payload)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_smoke_forecast(async_client) -> None:
    response = await async_client.get("/api/forecast", params={"scenario_id": "smoke", "horizon_hours": 12})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_smoke_explain_offline(async_client) -> None:
    result = run_scenario(ScenarioRequest())
    response = await async_client.post(
        "/api/explain",
        json={"scenario_id": result.scenario_id, "question": "What is the flat rate tariff price?", "result": result.model_dump()},
    )
    assert response.status_code == 200
    assert "sources" in response.json()


@pytest.mark.asyncio
async def test_smoke_offline_no_llm_key(async_client, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "")
    result = run_scenario(ScenarioRequest())
    response = await async_client.post(
        "/api/explain",
        json={"scenario_id": result.scenario_id, "question": "What is solar fraction?", "result": result.model_dump()},
    )
    assert response.status_code == 200
    assert os.getenv("OPENAI_API_KEY", "") == ""
