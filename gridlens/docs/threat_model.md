# GridLens Threat Model

| Risk | Description | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- | --- |
| Secret leakage | API keys or tokens could appear in logs, traces, or exception messages. | Medium | High | Structured logging redacts sensitive strings and offline mode avoids external calls by default. |
| Prompt injection | Malicious knowledge-base content could try to manipulate explanation prompts. | Medium | High | Prefer offline template answers, cite retrieved chunks, and constrain LLM prompts to provided context only. |
| Bad external data | Wrong fixture or adapter data could produce misleading outputs. | Medium | Medium | Version fixture data, validate schema, and document provenance. |
| Resource exhaustion | Very large horizon_hours values could increase runtime or memory use. | Medium | Medium | Enforce request limits with Pydantic and application settings. |
| Hallucination | An LLM explanation could invent scenario numbers or unsupported claims. | Medium | High | Default to deterministic offline answers and instruct any optional LLM to cite evidence and avoid invented numbers. |
| False precision | Forecast outputs may look more certain than they are. | High | Medium | Label the method as seasonal-naive and include explicit confidence notes and limitations. |
| Malicious documents | Markdown content could contain unsafe HTML or XSS payloads in downstream renderers. | Low | High | Treat knowledge docs as trusted repo content, sanitize any future user-supplied markdown, and avoid raw HTML rendering. |
