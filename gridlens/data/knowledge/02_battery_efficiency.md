# Battery Storage Efficiency and Degradation

Lithium-ion battery systems typically achieve round-trip efficiency in the 90% to 98% range, depending on inverter losses, operating temperature, charge rate, and cell chemistry. Higher efficiency means less energy lost between charging and discharging.

Depth of discharge limits matter for lifetime. Operators often keep state of charge within roughly 20% to 80% for long-life operation, even though the hardware may allow a wider usable window. Calendar aging occurs over time even with low usage, while cycle aging depends on charge and discharge throughput.

Temperature strongly affects performance and degradation. Cold conditions reduce available power and usable energy, while hot conditions accelerate aging. This GridLens implementation uses a simplified linear efficiency model and does not simulate detailed degradation.
