# Operations Runbook

## Startup

1. Install Python dependencies.
2. Run `python -m gridlens.rag.ingest` to build the local vector store.
3. Start the API with `uvicorn gridlens.app.main:app --host 0.0.0.0 --port 8000`.
4. Optionally start the UI with `python -m gridlens.ui.app`.

## Health checks

- API: `GET /health`
- Forecast sanity: `GET /api/forecast?scenario_id=default&horizon_hours=24`
- Retrieval sanity: `python -m gridlens.rag.ingest`

## Monitoring

- Watch structured logs for request duration, error category, and retrieval count.
- Alert on repeated explanation failures or missing knowledge ingestion.

## Troubleshooting

- **Import error**: verify dependencies from `gridlens/requirements.txt`.
- **Slow RAG startup**: first run downloads the embedding model.
- **Empty explanation results**: confirm knowledge files exist and ingest completed.
- **Validation failures**: check request horizon and scenario parameter bounds.

## Known failure modes

- Large first-run latency during model download.
- Empty retrieval for unsupported questions.
- Misleading forecast confidence if users over-interpret seasonal-naive outputs.
