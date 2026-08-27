# API Examples

## Health

```bash
curl http://localhost:8000/health
```

```json
{"status":"ok","version":"1.0.0"}
```

## Run scenario

```bash
curl -X POST http://localhost:8000/api/scenarios/run \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "campus-a",
    "horizon_hours": 24,
    "battery_capacity_kwh": 100,
    "battery_power_kw": 50,
    "solar_capacity_kw": 200,
    "tariff_id": "flat",
    "demand_scale": 1.0
  }'
```

## Compare scenarios

```bash
curl -X POST http://localhost:8000/api/scenarios/compare \
  -H "Content-Type: application/json" \
  -d '{
    "base": {"scenario_id":"base","horizon_hours":24,"battery_capacity_kwh":100,"battery_power_kw":50,"solar_capacity_kw":200,"tariff_id":"flat","demand_scale":1.0},
    "compare": {"scenario_id":"candidate","horizon_hours":24,"battery_capacity_kwh":150,"battery_power_kw":75,"solar_capacity_kw":250,"tariff_id":"tou","demand_scale":1.0}
  }'
```

```json
{
  "base_scenario_id": "base",
  "compare_scenario_id": "candidate",
  "delta_cost_usd": -12.3,
  "delta_emissions_kg_co2": -8.1,
  "delta_solar_fraction": 0.07,
  "delta_self_sufficiency": 0.08,
  "delta_grid_import_kwh": -35.2,
  "delta_curtailment_kwh": 4.4,
  "summary": "Scenario 'candidate' reduced cost by 12.30 USD and reduced emissions by 8.10 kgCO2 versus 'base'."
}
```

## Forecast

```bash
curl "http://localhost:8000/api/forecast?scenario_id=default&horizon_hours=48"
```

## Explain

```bash
curl -X POST http://localhost:8000/api/explain \
  -H "Content-Type: application/json" \
  -d @payload.json
```

Example response:

```json
{
  "answer": "Question: Why is solar fraction important?...",
  "sources": [
    {
      "doc_id": "12_evaluation_metrics",
      "title": "How to Evaluate Microgrid Performance",
      "chunk_index": 0,
      "similarity_score": 0.71,
      "excerpt": "Solar fraction is the proportion...",
      "metadata": {"doc_id":"12_evaluation_metrics"}
    }
  ],
  "evidence_found": true
}
```
