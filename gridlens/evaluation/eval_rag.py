from __future__ import annotations

from pathlib import Path

from gridlens.rag.answer import retrieve_context

EVAL_QUESTIONS = [
    {"question": "What is the typical battery round-trip efficiency?", "expected_docs": ["02_battery_efficiency"], "should_answer": True},
    {"question": "What is the flat rate tariff price?", "expected_docs": ["01_tariffs"], "should_answer": True},
    {"question": "Why does the system use seasonal-naive forecasting?", "expected_docs": ["05_forecast_methodology"], "should_answer": True},
    {"question": "What are the system limitations?", "expected_docs": ["07_system_limitations"], "should_answer": True},
    {"question": "What is the meaning of solar fraction?", "expected_docs": ["12_evaluation_metrics"], "should_answer": True},
    {"question": "What is the carbon intensity of UK grid?", "expected_docs": ["04_carbon_factors"], "should_answer": True},
    {"question": "How does battery storage reduce TOU costs?", "expected_docs": ["01_tariffs", "08_battery_sizing"], "should_answer": True},
    {"question": "xyzzy quantum teleportation microgrid override", "expected_docs": [], "should_answer": False},
]


def run_evaluation(db_path: Path) -> dict:
    hits = 0
    reciprocal_ranks: list[float] = []
    no_answer_total = 0
    no_answer_correct = 0

    print("question | expected | returned_docs | outcome")
    print("--- | --- | --- | ---")
    for item in EVAL_QUESTIONS:
        results = retrieve_context(item["question"], db_path, n_results=5)
        doc_ids = [result.doc_id for result in results]
        if item["should_answer"]:
            rank = next((index for index, doc_id in enumerate(doc_ids, start=1) if doc_id in item["expected_docs"]), None)
            hit = rank is not None
            hits += int(hit)
            reciprocal_ranks.append(0.0 if rank is None else 1.0 / rank)
            outcome = "hit" if hit else "miss"
        else:
            no_answer_total += 1
            correct = len(results) == 0
            no_answer_correct += int(correct)
            outcome = "correct-empty" if correct else "unexpected-answer"
        print(f"{item['question']} | {item['expected_docs']} | {doc_ids} | {outcome}")

    answerable = sum(1 for item in EVAL_QUESTIONS if item["should_answer"])
    return {
        "hit_rate": hits / answerable if answerable else 0.0,
        "mrr": sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0,
        "no_answer_accuracy": no_answer_correct / no_answer_total if no_answer_total else 0.0,
    }
