from dataclasses import dataclass
from typing import Any

from airline_cargo_optimization.solver import CargoOptimizationResult


@dataclass(frozen=True)
class CargoSolutionSummary:
    status: str
    aircraft_id: str
    selected_items: int
    total_revenue_usd: float
    total_weight_kg: float
    total_volume_m3: float
    weight_utilization_pct: float
    volume_utilization_pct: float


def build_solution_summary(
    result: CargoOptimizationResult,
    aircraft_config: dict[str, Any],
) -> CargoSolutionSummary:
    max_weight = float(aircraft_config["max_weight_kg"])
    max_volume = float(aircraft_config["max_volume_m3"])

    if max_weight <= 0:
        raise ValueError("La capacidad máxima de peso debe ser mayor que cero.")

    if max_volume <= 0:
        raise ValueError("La capacidad máxima de volumen debe ser mayor que cero.")

    return CargoSolutionSummary(
        status=result.status,
        aircraft_id=str(aircraft_config["aircraft_id"]),
        selected_items=len(result.selected_cargo),
        total_revenue_usd=result.total_revenue_usd,
        total_weight_kg=result.total_weight_kg,
        total_volume_m3=result.total_volume_m3,
        weight_utilization_pct=(result.total_weight_kg / max_weight) * 100,
        volume_utilization_pct=(result.total_volume_m3 / max_volume) * 100,
    )
