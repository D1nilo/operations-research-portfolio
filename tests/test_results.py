import pandas as pd
import pytest

from airline_cargo_optimization.results import (
    build_solution_summary,
)
from airline_cargo_optimization.solver import (
    CargoOptimizationResult,
)


def create_result() -> CargoOptimizationResult:
    selected_cargo = pd.DataFrame(
        {
            "cargo_id": ["C001", "C002"],
            "weight_kg": [400, 600],
            "volume_m3": [2.0, 3.0],
            "revenue_usd": [5000, 7000],
        }
    )

    return CargoOptimizationResult(
        status="OPTIMAL",
        objective_value=12000,
        selected_cargo=selected_cargo,
        total_weight_kg=1000,
        total_volume_m3=5.0,
        total_revenue_usd=12000,
    )


def create_config() -> dict[str, object]:
    return {
        "aircraft_id": "TEST-001",
        "max_weight_kg": 2000,
        "max_volume_m3": 10.0,
    }


def test_build_solution_summary_calculates_utilization() -> None:
    summary = build_solution_summary(
        create_result(),
        create_config(),
    )

    assert summary.status == "OPTIMAL"
    assert summary.selected_items == 2
    assert summary.weight_utilization_pct == 50.0
    assert summary.volume_utilization_pct == 50.0


def test_build_solution_summary_rejects_zero_weight_capacity() -> None:
    config = create_config()
    config["max_weight_kg"] = 0

    with pytest.raises(
        ValueError,
        match="peso",
    ):
        build_solution_summary(
            create_result(),
            config,
        )


def test_build_solution_summary_rejects_zero_volume_capacity() -> None:
    config = create_config()
    config["max_volume_m3"] = 0

    with pytest.raises(
        ValueError,
        match="volumen",
    ):
        build_solution_summary(
            create_result(),
            config,
        )