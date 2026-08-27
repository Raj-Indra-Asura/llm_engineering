from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from gridlens.domain.models import HourlyRecord, ScenarioRequest, ScenarioResult

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "data" / "fixtures"


def _load_json(filename: str) -> dict:
    with (FIXTURES_DIR / filename).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _fixture_start_timestamp(start_timestamp: str) -> datetime:
    return datetime.fromisoformat(start_timestamp.replace("Z", "+00:00"))


def _format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _resolve_tariff(tariffs: dict, tariff_id: str, hour: int) -> tuple[float, float]:
    profiles = tariffs["profiles"]
    if tariff_id not in profiles:
        raise ValueError(f"Unsupported tariff_id: {tariff_id}")

    profile = profiles[tariff_id]
    export_rate = float(profile["export_usd_kwh"])
    schedule = profile.get("schedule")
    if schedule is None:
        return float(profile["import_usd_kwh"]), export_rate

    hour_of_day = hour % 24
    peak_hours = set(schedule["peak_hours"])
    if hour_of_day in peak_hours:
        return float(schedule["peak_import_usd_kwh"]), export_rate
    return float(schedule["offpeak_import_usd_kwh"]), export_rate


def run_scenario(request: ScenarioRequest) -> ScenarioResult:
    load_profile = _load_json("load_profile.json")
    solar_profile = _load_json("solar_profile.json")
    carbon_profile = _load_json("carbon_intensity.json")
    tariffs = _load_json("tariffs.json")

    load_values = load_profile["values"]
    solar_values = solar_profile["values"]
    carbon_values = carbon_profile["values"]
    fixture_length = min(len(load_values), len(solar_values), len(carbon_values))
    start_timestamp = _fixture_start_timestamp(load_profile["start_timestamp"])

    soc = request.battery_initial_soc
    records: list[HourlyRecord] = []
    warnings: list[str] = []
    constraint_violations: list[str] = []

    total_demand = 0.0
    total_solar = 0.0
    total_solar_to_load = 0.0
    total_battery_throughput = 0.0
    total_grid_import = 0.0
    total_grid_export = 0.0
    total_curtailment = 0.0
    total_cost = 0.0
    total_emissions = 0.0
    energy_balance_error = 0.0
    peak_demand = 0.0

    if request.horizon_hours > fixture_length:
        warnings.append("Simulation horizon exceeds fixture length; profiles repeat cyclically.")

    for hour in range(request.horizon_hours):
        index = hour % fixture_length
        demand = float(load_values[index]) * request.demand_scale
        solar_available = float(solar_values[index]) * request.solar_capacity_kw * request.solar_derating
        carbon_intensity = float(carbon_values[index])
        tariff_import, tariff_export = _resolve_tariff(tariffs, request.tariff_id, hour)

        battery_charge = 0.0
        battery_discharge = 0.0
        grid_import = 0.0
        grid_export = 0.0
        curtailment = 0.0

        if solar_available >= demand:
            surplus = solar_available - demand
            if request.battery_capacity_kwh > 0.0 and request.battery_power_kw > 0.0:
                charge_room_input = ((1.0 - soc) * request.battery_capacity_kwh) / request.battery_efficiency
                battery_charge = min(surplus, request.battery_power_kw, max(0.0, charge_room_input))
                soc += (battery_charge * request.battery_efficiency) / request.battery_capacity_kwh
            remaining_surplus = surplus - battery_charge
            grid_export = max(0.0, remaining_surplus)
            curtailment = max(0.0, remaining_surplus - grid_export)
        else:
            deficit = demand - solar_available
            if request.battery_capacity_kwh > 0.0 and request.battery_power_kw > 0.0:
                available_discharge = soc * request.battery_capacity_kwh * request.battery_efficiency
                battery_discharge = min(deficit, request.battery_power_kw, max(0.0, available_discharge))
                soc -= battery_discharge / request.battery_efficiency / request.battery_capacity_kwh
            grid_import = max(0.0, deficit - battery_discharge)

        soc = min(1.0, max(0.0, soc))
        cost = (grid_import * tariff_import) - (grid_export * tariff_export)
        emissions = grid_import * carbon_intensity
        timestamp = _format_timestamp(start_timestamp + timedelta(hours=hour))

        if not 0.0 <= soc <= 1.0:
            constraint_violations.append(f"Hour {hour}: state of charge out of bounds ({soc}).")

        solar_to_load = min(demand, solar_available)
        hourly_balance = abs(
            (solar_available + grid_import + battery_discharge)
            - (demand + battery_charge + grid_export + curtailment)
        )

        total_demand += demand
        total_solar += solar_available
        total_solar_to_load += solar_to_load
        total_battery_throughput += battery_charge + battery_discharge
        total_grid_import += grid_import
        total_grid_export += grid_export
        total_curtailment += curtailment
        total_cost += cost
        total_emissions += emissions
        energy_balance_error += hourly_balance
        peak_demand = max(peak_demand, demand)

        records.append(
            HourlyRecord(
                hour=hour,
                timestamp=timestamp,
                demand_kw=demand,
                solar_gen_kw=solar_available,
                battery_charge_kw=battery_charge,
                battery_discharge_kw=battery_discharge,
                soc=soc,
                grid_import_kw=grid_import,
                grid_export_kw=grid_export,
                curtailment_kw=curtailment,
                cost_usd=cost,
                emissions_kg_co2=emissions,
                tariff_usd_kwh=tariff_import,
                carbon_intensity_kg_kwh=carbon_intensity,
            )
        )

    solar_fraction = total_solar_to_load / total_demand if total_demand else 0.0
    self_sufficiency = (total_demand - total_grid_import) / total_demand if total_demand else 0.0

    return ScenarioResult(
        scenario_id=request.scenario_id,
        request=request,
        records=records,
        total_demand_kwh=total_demand,
        total_solar_kwh=total_solar,
        total_battery_throughput_kwh=total_battery_throughput,
        total_grid_import_kwh=total_grid_import,
        total_grid_export_kwh=total_grid_export,
        total_curtailment_kwh=total_curtailment,
        total_cost_usd=total_cost,
        total_emissions_kg_co2=total_emissions,
        peak_demand_kw=peak_demand,
        solar_fraction=solar_fraction,
        self_sufficiency=self_sufficiency,
        energy_balance_error_kwh=energy_balance_error,
        constraint_violations=constraint_violations,
        warnings=warnings,
        computed_at=_format_timestamp(start_timestamp + timedelta(hours=request.horizon_hours)),
    )
