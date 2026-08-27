# 5-Minute Demo Script

1. Start the API: `uvicorn gridlens.app.main:app --reload`
2. Start the UI: `python -m gridlens.ui.app`
3. Open the Scenario tab and set a baseline battery, solar, tariff, and horizon.
4. Click **Run Scenario** and narrate the demand, solar, grid, and battery SoC plots.
5. Open the Forecast tab and show the offline seasonal-naive forecast chart.
6. Open the Compare tab, create a larger battery / solar case, and explain the KPI delta table.
7. Open the Explanation tab and ask: “What is solar fraction?” or “How do batteries reduce TOU costs?”
8. Highlight the cited sources and note that the default explanation path stays offline.
