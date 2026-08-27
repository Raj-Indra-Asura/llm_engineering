# Energy Balance and Conservation Laws

For every simulated hour, the site energy balance should close. A simplified balance can be written as:

Demand = Solar_used + Battery_discharge - Battery_charge + Grid_import - Grid_export + Curtailment

In practice, simulators track each term separately and verify that numerical error remains small. GridLens treats balance errors above 0.01 kWh as warning-worthy because they may indicate a bug, inconsistent units, or a sign convention issue.

Curtailment occurs when available solar exceeds demand plus battery charging capability plus any allowed export path. A correct balance check is a basic integrity safeguard for scenario analysis.
