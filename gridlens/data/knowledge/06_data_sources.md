# Data Sources and Provenance

GridLens uses synthetic fixture data that is modeled on several real-world reference sources rather than live operational feeds. The demand profile resembles UK university campus consumption patterns, the solar profile reflects clear-sky generation near 51.5°N, the carbon profile is inspired by UK National Grid ESO carbon intensity data, and tariff values are aligned to Ofgem industrial and commercial benchmark ranges.

The fixture data is versioned with the codebase and can be validated through automated tests. This makes scenario results reproducible across environments.

Optional adapters for Open-Meteo weather data and PVGIS solar estimates can be layered on top later, but the default application behavior remains fully offline and deterministic.
