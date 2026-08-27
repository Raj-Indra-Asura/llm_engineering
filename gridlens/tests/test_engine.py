from __future__ import annotations

from pydantic import ValidationError
import pytest

from gridlens.domain.engine import run_scenario
from gridlens.domain.forecast import run_forecast
from gridlens.domain.models import ScenarioRequest


def test_energy_conservation(default_request: ScenarioRequest) -> None:
    result = run_scenario(default_request)
    assert result.energy_balance_error_kwh < 0.01


def test_battery_soc_limits(default_request: ScenarioRequest) -> None:
    result = run_scenario(default_request)
    assert all(0.0 <= record.soc <= 1.0 for record in result.records)


def test_zero_storage(default_request: ScenarioRequest) -> None:
    request = default_request.model_copy(update={"battery_capacity_kwh": 0.0})
    result = run_scenario(request)

    expected_grid_import = sum(max(0.0, record.demand_kw - record.solar_gen_kw) for record in result.records)
    assert result.total_battery_throughput_kwh == pytest.approx(0.0)
    assert all(record.battery_discharge_kw == pytest.approx(0.0) for record in result.records)
    assert result.total_grid_import_kwh == pytest.approx(expected_grid_import)


def test_zero_renewable(default_request: ScenarioRequest) -> None:
    request = default_request.model_copy(update={"solar_capacity_kw": 0.0})
    result = run_scenario(request)

    assert result.total_solar_kwh == pytest.approx(0.0)
    assert result.total_grid_import_kwh + sum(record.battery_discharge_kw for record in result.records) == pytest.approx(
        result.total_demand_kwh
    )


def test_emissions_positive(default_request: ScenarioRequest) -> None:
    result = run_scenario(default_request)
    assert result.total_emissions_kg_co2 >= 0.0


def test_forecast_shape(default_request: ScenarioRequest) -> None:
    forecast = run_forecast(default_request)
    assert forecast.method == "seasonal_naive"
    assert len(forecast.forecasted_demand_kw) == default_request.horizon_hours
    assert len(forecast.forecasted_solar_kw) == default_request.horizon_hours
    assert len(forecast.timestamps) == default_request.horizon_hours


def test_invalid_horizon() -> None:
    with pytest.raises(ValidationError):
        ScenarioRequest(horizon_hours=0)


def test_reproducibility(default_request: ScenarioRequest) -> None:
    result_a = run_scenario(default_request)
    result_b = run_scenario(default_request)
    assert result_a.model_dump() == result_b.model_dump()


def test_tariff_tou(default_request: ScenarioRequest) -> None:
    request = default_request.model_copy(update={"tariff_id": "tou"})
    result = run_scenario(request)
    assert len(result.records) == request.horizon_hours
    assert result.total_cost_usd >= 0.0
