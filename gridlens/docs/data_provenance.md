# Data Provenance

## Fixture sources

- **load_profile.json**: synthetic hourly campus demand profile based on typical UK university load shapes.
- **solar_profile.json**: synthetic clear-sky solar availability aligned to a latitude near 51.5°N.
- **carbon_intensity.json**: synthetic hourly carbon intensity values inspired by UK National Grid ESO patterns.
- **tariffs.json**: simplified flat and time-of-use tariffs aligned to Ofgem I&C benchmark ranges.

## Versioning

All fixture files are stored in the repository and change through version control. This allows deterministic replay of scenario outputs across environments.

## Validation methodology

- Schema validation through Pydantic request and response models
- Regression tests for energy balance, forecast shapes, and reproducibility
- Explicit documentation of the simplified modeling assumptions
