from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class ScenarioRequest(BaseModel):
    scenario_id: str = Field(default="default", description="Unique scenario identifier")
    horizon_hours: int = Field(default=24, ge=1, le=168, description="Simulation horizon in hours")
    battery_capacity_kwh: float = Field(default=100.0, ge=0.0, le=10000.0)
    battery_power_kw: float = Field(default=50.0, ge=0.0, le=5000.0)
    battery_initial_soc: float = Field(default=0.5, ge=0.0, le=1.0, description="Initial state of charge 0-1")
    battery_efficiency: float = Field(default=0.95, ge=0.5, le=1.0)
    solar_capacity_kw: float = Field(default=200.0, ge=0.0, le=50000.0)
    solar_derating: float = Field(default=0.85, ge=0.0, le=1.0, description="Performance ratio / derating factor")
    tariff_id: str = Field(default="flat", description="Tariff profile to use")
    demand_scale: float = Field(default=1.0, ge=0.1, le=10.0)
    data_source: str = Field(default="fixture", description="fixture or api")

    @field_validator("scenario_id")
    @classmethod
    def validate_scenario_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("scenario_id must not be empty")
        return value

    @field_validator("tariff_id")
    @classmethod
    def validate_tariff_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("tariff_id must not be empty")
        return value

    @field_validator("data_source")
    @classmethod
    def validate_data_source(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"fixture", "api"}:
            raise ValueError("data_source must be 'fixture' or 'api'")
        return normalized


class HourlyRecord(BaseModel):
    hour: int
    timestamp: str
    demand_kw: float
    solar_gen_kw: float
    battery_charge_kw: float
    battery_discharge_kw: float
    soc: float
    grid_import_kw: float
    grid_export_kw: float
    curtailment_kw: float
    cost_usd: float
    emissions_kg_co2: float
    tariff_usd_kwh: float
    carbon_intensity_kg_kwh: float


class ScenarioResult(BaseModel):
    scenario_id: str
    request: ScenarioRequest
    records: list[HourlyRecord]
    total_demand_kwh: float
    total_solar_kwh: float
    total_battery_throughput_kwh: float
    total_grid_import_kwh: float
    total_grid_export_kwh: float
    total_curtailment_kwh: float
    total_cost_usd: float
    total_emissions_kg_co2: float
    peak_demand_kw: float
    solar_fraction: float
    self_sufficiency: float
    energy_balance_error_kwh: float
    constraint_violations: list[str]
    warnings: list[str]
    computed_at: str


class ForecastResult(BaseModel):
    scenario_id: str
    method: str
    horizon_hours: int
    forecasted_demand_kw: list[float]
    forecasted_solar_kw: list[float]
    timestamps: list[str]
    confidence_note: str


class ScenarioComparison(BaseModel):
    base_scenario_id: str
    compare_scenario_id: str
    delta_cost_usd: float
    delta_emissions_kg_co2: float
    delta_solar_fraction: float
    delta_self_sufficiency: float
    delta_grid_import_kwh: float
    delta_curtailment_kwh: float
    summary: str


class ScenarioComparisonRequest(BaseModel):
    base: ScenarioRequest
    compare: ScenarioRequest


class SourceReference(BaseModel):
    doc_id: str
    title: str
    chunk_index: int
    similarity_score: float
    excerpt: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExplainRequest(BaseModel):
    scenario_id: str
    question: str
    result: ScenarioResult
