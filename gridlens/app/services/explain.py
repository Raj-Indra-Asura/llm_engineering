from __future__ import annotations

import os
from pathlib import Path

from gridlens.domain.models import ScenarioResult
from gridlens.rag.answer import retrieve_context


def _format_sources(sources: list[dict]) -> str:
    return "\n".join(
        f"- [{index}] {source['title']} (chunk {source['chunk_index']}, score={source['similarity_score']:.3f})"
        for index, source in enumerate(sources, start=1)
    )


def _scenario_summary(result: ScenarioResult) -> str:
    return (
        f"Scenario '{result.scenario_id}' total cost is {result.total_cost_usd:.2f} USD, "
        f"total emissions are {result.total_emissions_kg_co2:.2f} kgCO2, "
        f"solar fraction is {result.solar_fraction:.3f}, and self-sufficiency is {result.self_sufficiency:.3f}."
    )


def _offline_answer(result: ScenarioResult, question: str, sources: list[dict]) -> str:
    cited_titles = ", ".join(sorted({source["title"] for source in sources}))
    return (
        f"Question: {question}\n\n"
        f"{_scenario_summary(result)}\n\n"
        f"Relevant knowledge documents: {cited_titles}.\n"
        f"Use the cited material below to interpret the deterministic scenario outcome:\n"
        f"{_format_sources(sources)}"
    )


def explain_scenario(
    result: ScenarioResult,
    question: str,
    db_path: Path,
    use_llm: bool = False,
    llm_model: str = "gpt-4o-mini",
) -> dict:
    sources = [source.model_dump() for source in retrieve_context(question, db_path)]
    if not sources:
        return {
            "answer": "Insufficient evidence in knowledge base to answer this question.",
            "sources": [],
            "evidence_found": False,
        }

    if not use_llm:
        return {
            "answer": _offline_answer(result, question, sources),
            "sources": sources,
            "evidence_found": True,
        }

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return {
            "answer": _offline_answer(result, question, sources),
            "sources": sources,
            "evidence_found": True,
        }

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    source_blocks = "\n\n".join(
        f"[{index}] {source['title']}\n{source['excerpt']}" for index, source in enumerate(sources, start=1)
    )
    completion = client.chat.completions.create(
        model=llm_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You explain GridLens scenario results. Cite sources like [1]. "
                    "Do not invent scenario numbers or unsupported claims."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Scenario summary: {_scenario_summary(result)}\n"
                    f"Question: {question}\n\n"
                    f"Retrieved context:\n{source_blocks}"
                ),
            },
        ],
    )
    return {
        "answer": completion.choices[0].message.content or _offline_answer(result, question, sources),
        "sources": sources,
        "evidence_found": True,
    }
