# Known Limitations

GridLens is a planning-oriented microgrid tool with intentional simplifications:

1. **Hourly resolution only**: intra-hour peaks, ramping, and control dynamics are not represented.
2. **Single-node grid interaction**: the engine does not model feeders, transformers, voltage, or congestion.
3. **Simplified storage physics**: battery degradation, temperature, nonlinear efficiency, and auxiliary load are excluded.
4. **Deterministic fixtures**: default results reflect versioned synthetic data rather than live telemetry.
5. **Seasonal-naive forecast**: unusual weather, outages, and holiday behavior are not learned.
6. **Single-asset logic**: no portfolio optimization across multiple batteries, solar fields, or EV fleets.
7. **Explanation evidence scope**: answers are limited to the bundled knowledge base and may intentionally refuse unsupported questions.
