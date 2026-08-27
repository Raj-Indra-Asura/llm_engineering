# GridLens

GridLens is a microgrid scenario planning application that combines a deterministic energy simulation engine with retrieval-augmented explanations. It supports scenario runs, scenario comparison, offline forecasting, evidence-based explanations, and an offline Gradio UI.

## Architecture

```text
Client / UI / API
        |
        v
FastAPI routers ----> Gradio Blocks UI
        |
        v
Deterministic domain engine ----> Scenario / Forecast results
        |
        +----> RAG retrieval ----> Explanation service
                     |
                     v
              Chroma + sentence-transformers
```

## Quick start

### Local

```bash
cd gridlens
python -m pytest tests -v
uvicorn gridlens.app.main:app --reload
python -m gridlens.ui.app
```

### Docker

```bash
cd gridlens
docker build -t gridlens .
docker run -p 8000:8000 gridlens
```

## API endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | /health | Health check |
| POST | /api/scenarios/run | Run a deterministic scenario |
| POST | /api/scenarios/compare | Compare two scenarios and return KPI deltas |
| GET | /api/forecast | Return a deterministic seasonal-naive forecast |
| POST | /api/explain | Return an evidence-based explanation using the local knowledge base |

## Gradio UI

Run:

```bash
python -m gridlens.ui.app
```

The UI provides scenario, forecast, compare, and explanation tabs with offline charts and evidence lookup.

## Tests

```bash
python -m pytest gridlens/tests -v
```

## Environment variables

| Variable | Purpose | Default |
| --- | --- | --- |
| OPENAI_API_KEY | Optional key for LLM explanations | empty |
| LOG_LEVEL | API logging level | INFO |
| CORS_ORIGINS | Allowed browser origins | localhost UI ports |
