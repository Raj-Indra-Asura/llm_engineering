from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from gridlens.domain.models import ForecastResult, ScenarioRequest

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "data" / "fixtures"


def _load_json(filename: str) -> dict:
    with (FIXTURES_DIR / filename).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def run_forecast(request: ScenarioRequest) -> ForecastResult:
    load_profile = _load_json("load_profile.json")
    solar_profile = _load_json("solar_profile.json")
    load_values = load_profile["values"]
    solar_values = solar_profile["values"]
    fixture_length = min(len(load_values), len(solar_values))
    start_timestamp = datetime.fromisoformat(load_profile["start_timestamp"].replace("Z", "+00:00"))

    forecasted_demand_kw: list[float] = []
    forecasted_solar_kw: list[float] = []
    timestamps: list[str] = []

    for hour in range(request.horizon_hours):
        index = hour % fixture_length
        forecasted_demand_kw.append(float(load_values[index]) * request.demand_scale)
        forecasted_solar_kw.append(
            float(solar_values[index]) * request.solar_capacity_kw * request.solar_derating
        )
        timestamps.append(_format_timestamp(start_timestamp + timedelta(hours=hour)))

    return ForecastResult(
        scenario_id=request.scenario_id,
        method="seasonal_naive",
        horizon_hours=request.horizon_hours,
        forecasted_demand_kw=forecasted_demand_kw,
        forecasted_solar_kw=forecasted_solar_kw,
        timestamps=timestamps,
        confidence_note="Seasonal-naive forecast repeating the deterministic 48-hour fixture pattern.",
    )
