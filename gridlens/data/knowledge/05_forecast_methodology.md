# Energy Demand and Solar Forecast Methods

Seasonal-naive forecasting repeats a previous pattern, such as the same hour last day or the same hour last week. It is simple, fully offline, and requires no model training. This makes it useful for deterministic planning tools and demos.

A rolling mean forecast averages the last N observations to smooth noise, but it can lag fast changes. More advanced machine learning approaches may combine weather forecasts, calendar features, and site telemetry to improve accuracy.

The main limitation of seasonal-naive forecasting is that it misses unusual weather, holidays, outages, and sudden load changes. GridLens uses a seasonal-naive method with a 24-hour period because it is reproducible and works without external services.
