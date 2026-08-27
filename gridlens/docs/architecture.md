# GridLens Architecture

## Component diagram

```text
gridlens/
  app/        FastAPI app, routers, middleware, logging, config, explanation service
  domain/     Deterministic scenario engine, forecast logic, Pydantic models
  rag/        Knowledge ingestion, embedding retrieval, source references
  ui/         Gradio Blocks interface with Plotly charts
  data/       Versioned fixture data and knowledge documents
  evaluation/ Retrieval evaluation harness
  tests/      Unit, integration, RAG, and smoke coverage
```

## Data flow

1. A request enters FastAPI or the Gradio callback layer.
2. The domain engine computes deterministic hourly records and KPI summaries.
3. Forecast requests use the offline seasonal-naive forecaster.
4. Optional explanation requests ingest or query the knowledge base.
5. Retrieved chunks become cited evidence for an offline template answer, or for an optional LLM path.
6. Results are returned as structured Pydantic responses or rendered in Plotly charts.

## Technology choices

- **FastAPI**: simple typed HTTP interfaces and automatic validation.
- **Pydantic**: structured scenario, forecast, comparison, and source outputs.
- **Plotly + Gradio**: offline interactive visualization and operator-facing UI.
- **sentence-transformers**: local embeddings without external LLM APIs.
- **ChromaDB**: lightweight persistent vector store with metadata.

## Week mapping

- **Week 1**: deterministic domain engine and API baseline
- **Week 2**: compare endpoint, forecast endpoint, Gradio interface
- **Week 3**: RAG documents, chunking, embeddings, retrieval
- **Week 4**: explanation service and integration flows
- **Week 5**: production safeguards, evaluation, docs, Docker packaging
