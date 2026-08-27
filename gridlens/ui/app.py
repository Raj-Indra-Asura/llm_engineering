from __future__ import annotations

from pathlib import Path

import gradio as gr
import plotly.graph_objects as go

from gridlens.app.services.explain import explain_scenario
from gridlens.domain.engine import run_scenario
from gridlens.domain.forecast import run_forecast
from gridlens.domain.models import ScenarioRequest
from gridlens.rag.ingest import ingest_knowledge_base

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = ROOT / "data" / "knowledge"
DB_PATH = ROOT / "data" / "chroma_db"


def _blank_figure(title: str, message: str) -> go.Figure:
    figure = go.Figure()
    figure.update_layout(title=title, template="plotly_white")
    figure.add_annotation(text=message, x=0.5, y=0.5, showarrow=False, xref="paper", yref="paper")
    return figure


def _scenario_figure(result) -> go.Figure:
    figure = go.Figure()
    timestamps = [record.timestamp for record in result.records]
    figure.add_trace(go.Scatter(x=timestamps, y=[record.demand_kw for record in result.records], name="Demand kW"))
    figure.add_trace(go.Scatter(x=timestamps, y=[record.solar_gen_kw for record in result.records], name="Solar kW"))
    figure.add_trace(
        go.Bar(x=timestamps, y=[record.grid_import_kw for record in result.records], name="Grid import kW", opacity=0.6)
    )
    figure.add_trace(
        go.Bar(x=timestamps, y=[-record.grid_export_kw for record in result.records], name="Grid export kW", opacity=0.6)
    )
    figure.update_layout(title="Demand, solar, and grid exchange", barmode="relative", template="plotly_white")
    return figure


def _soc_figure(result) -> go.Figure:
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=[record.timestamp for record in result.records],
            y=[record.soc * 100 for record in result.records],
            name="Battery SoC %",
        )
    )
    figure.update_layout(title="Battery state of charge", template="plotly_white", yaxis_title="SoC %")
    return figure


def _forecast_figure(result) -> go.Figure:
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=result.timestamps, y=result.forecasted_demand_kw, name="Forecast demand kW"))
    figure.add_trace(go.Scatter(x=result.timestamps, y=result.forecasted_solar_kw, name="Forecast solar kW"))
    figure.update_layout(title="Forecasted demand and solar", template="plotly_white")
    return figure


def _kpi_summary(result) -> dict:
    return {
        "total_cost_usd": round(result.total_cost_usd, 4),
        "total_emissions_kg_co2": round(result.total_emissions_kg_co2, 4),
        "solar_fraction": round(result.solar_fraction, 4),
        "self_sufficiency": round(result.self_sufficiency, 4),
    }


def _build_request(
    battery_capacity_kwh: float,
    battery_power_kw: float,
    solar_capacity_kw: float,
    demand_scale: float,
    tariff_id: str,
    horizon_hours: int,
    scenario_id: str = "default",
) -> ScenarioRequest:
    return ScenarioRequest(
        scenario_id=scenario_id,
        battery_capacity_kwh=battery_capacity_kwh,
        battery_power_kw=battery_power_kw,
        solar_capacity_kw=solar_capacity_kw,
        demand_scale=demand_scale,
        tariff_id=tariff_id,
        horizon_hours=int(horizon_hours),
    )


def run_scenario_ui(*args):
    gr.Info("Running scenario...")
    try:
        result = run_scenario(_build_request(*args))
    except Exception as exc:
        gr.Warning(f"Scenario failed: {exc}")
        return (
            _blank_figure("Demand, solar, and grid exchange", "Unable to run scenario."),
            _blank_figure("Battery state of charge", "Unable to run scenario."),
            {},
            f"Error: {exc}",
        )
    return _scenario_figure(result), _soc_figure(result), _kpi_summary(result), "Scenario completed."


def run_forecast_ui(*args):
    gr.Info("Running forecast...")
    try:
        result = run_forecast(_build_request(*args))
    except Exception as exc:
        gr.Warning(f"Forecast failed: {exc}")
        return _blank_figure("Forecasted demand and solar", "Unable to run forecast."), f"Error: {exc}"
    return _forecast_figure(result), result.confidence_note


def run_compare_ui(
    base_capacity: float,
    base_power: float,
    base_solar: float,
    base_demand: float,
    base_tariff: str,
    base_horizon: int,
    compare_capacity: float,
    compare_power: float,
    compare_solar: float,
    compare_demand: float,
    compare_tariff: str,
    compare_horizon: int,
):
    gr.Info("Comparing scenarios...")
    try:
        base_request = _build_request(
            base_capacity,
            base_power,
            base_solar,
            base_demand,
            base_tariff,
            base_horizon,
            scenario_id="base",
        )
        compare_request = _build_request(
            compare_capacity,
            compare_power,
            compare_solar,
            compare_demand,
            compare_tariff,
            compare_horizon,
            scenario_id="compare",
        )
        base_result = run_scenario(base_request)
        compare_result = run_scenario(compare_request)
    except Exception as exc:
        gr.Warning(f"Comparison failed: {exc}")
        return {}, {}, [], f"Error: {exc}"

    deltas = [
        ["total_cost_usd", round(base_result.total_cost_usd, 4), round(compare_result.total_cost_usd, 4), round(compare_result.total_cost_usd - base_result.total_cost_usd, 4)],
        ["total_emissions_kg_co2", round(base_result.total_emissions_kg_co2, 4), round(compare_result.total_emissions_kg_co2, 4), round(compare_result.total_emissions_kg_co2 - base_result.total_emissions_kg_co2, 4)],
        ["solar_fraction", round(base_result.solar_fraction, 4), round(compare_result.solar_fraction, 4), round(compare_result.solar_fraction - base_result.solar_fraction, 4)],
        ["self_sufficiency", round(base_result.self_sufficiency, 4), round(compare_result.self_sufficiency, 4), round(compare_result.self_sufficiency - base_result.self_sufficiency, 4)],
    ]
    return _kpi_summary(base_result), _kpi_summary(compare_result), deltas, "Comparison completed."


def explain_ui(*args):
    gr.Info("Searching the knowledge base...")
    ingest_knowledge_base(KNOWLEDGE_DIR, DB_PATH)
    question = args[-1]
    try:
        result = run_scenario(_build_request(*args[:-1]))
        explanation = explain_scenario(result, question, DB_PATH, use_llm=False)
    except Exception as exc:
        gr.Warning(f"Explanation failed: {exc}")
        return "Error while generating explanation.", "No sources."

    if not explanation["evidence_found"]:
        return explanation["answer"], "No evidence found."

    sources = "\n".join(
        f"- {source['title']} (chunk {source['chunk_index']}, score={source['similarity_score']:.3f})"
        for source in explanation["sources"]
    )
    return explanation["answer"], sources


def build_app() -> gr.Blocks:
    with gr.Blocks(title="GridLens") as demo:
        gr.Markdown("# GridLens\nOffline microgrid scenario planning and explanation workspace.")
        with gr.Row():
            battery_capacity = gr.Slider(0, 500, value=100, step=5, label="Battery capacity (kWh)")
            battery_power = gr.Slider(0, 200, value=50, step=5, label="Battery power (kW)")
            solar_capacity = gr.Slider(0, 500, value=200, step=5, label="Solar capacity (kW)")
        with gr.Row():
            demand_scale = gr.Slider(0.5, 2.0, value=1.0, step=0.05, label="Demand scale")
            tariff_id = gr.Dropdown(["flat", "tou"], value="flat", label="Tariff")
            horizon_hours = gr.Number(value=24, label="Horizon hours", precision=0)

        with gr.Tab("Scenario"):
            run_button = gr.Button("Run Scenario")
            scenario_plot = gr.Plot(value=_blank_figure("Demand, solar, and grid exchange", "Run a scenario to see results."))
            soc_plot = gr.Plot(value=_blank_figure("Battery state of charge", "Run a scenario to see results."))
            kpi_json = gr.JSON(value={})
            scenario_status = gr.Markdown("Ready.")
            run_button.click(
                fn=run_scenario_ui,
                inputs=[battery_capacity, battery_power, solar_capacity, demand_scale, tariff_id, horizon_hours],
                outputs=[scenario_plot, soc_plot, kpi_json, scenario_status],
            )

        with gr.Tab("Forecast"):
            forecast_button = gr.Button("Run Forecast")
            forecast_plot = gr.Plot(value=_blank_figure("Forecasted demand and solar", "Run a forecast to see results."))
            forecast_status = gr.Markdown("Ready.")
            forecast_button.click(
                fn=run_forecast_ui,
                inputs=[battery_capacity, battery_power, solar_capacity, demand_scale, tariff_id, horizon_hours],
                outputs=[forecast_plot, forecast_status],
            )

        with gr.Tab("Compare"):
            gr.Markdown("Compare two scenarios side by side.")
            with gr.Row():
                base_capacity = gr.Slider(0, 500, value=100, step=5, label="Base battery capacity (kWh)")
                base_power = gr.Slider(0, 200, value=50, step=5, label="Base battery power (kW)")
                base_solar = gr.Slider(0, 500, value=200, step=5, label="Base solar capacity (kW)")
                base_demand = gr.Slider(0.5, 2.0, value=1.0, step=0.05, label="Base demand scale")
                base_tariff = gr.Dropdown(["flat", "tou"], value="flat", label="Base tariff")
                base_horizon = gr.Number(value=24, label="Base horizon", precision=0)
            with gr.Row():
                compare_capacity = gr.Slider(0, 500, value=150, step=5, label="Compare battery capacity (kWh)")
                compare_power = gr.Slider(0, 200, value=75, step=5, label="Compare battery power (kW)")
                compare_solar = gr.Slider(0, 500, value=250, step=5, label="Compare solar capacity (kW)")
                compare_demand = gr.Slider(0.5, 2.0, value=1.0, step=0.05, label="Compare demand scale")
                compare_tariff = gr.Dropdown(["flat", "tou"], value="tou", label="Compare tariff")
                compare_horizon = gr.Number(value=24, label="Compare horizon", precision=0)
            compare_button = gr.Button("Compare")
            base_json = gr.JSON(value={})
            compare_json = gr.JSON(value={})
            delta_table = gr.Dataframe(headers=["metric", "base", "compare", "delta"], value=[])
            compare_status = gr.Markdown("Ready.")
            compare_button.click(
                fn=run_compare_ui,
                inputs=[
                    base_capacity,
                    base_power,
                    base_solar,
                    base_demand,
                    base_tariff,
                    base_horizon,
                    compare_capacity,
                    compare_power,
                    compare_solar,
                    compare_demand,
                    compare_tariff,
                    compare_horizon,
                ],
                outputs=[base_json, compare_json, delta_table, compare_status],
            )

        with gr.Tab("Explanation"):
            question = gr.Textbox(label="Question", placeholder="Why is cost higher in this scenario?")
            ask_button = gr.Button("Ask")
            answer_markdown = gr.Markdown("Ask a question to retrieve evidence-based guidance.")
            source_markdown = gr.Markdown("Sources will appear here.")
            ask_button.click(
                fn=explain_ui,
                inputs=[battery_capacity, battery_power, solar_capacity, demand_scale, tariff_id, horizon_hours, question],
                outputs=[answer_markdown, source_markdown],
            )

    return demo


app = build_app()
demo = app


if __name__ == "__main__":
    demo.launch()
