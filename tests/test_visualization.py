from pathlib import Path

import pandas as pd
import pytest

from airline_cargo_optimization.results import CargoSolutionSummary
from airline_cargo_optimization.solver import CargoOptimizationResult
from airline_cargo_optimization.visualization import (
    create_capacity_utilization_chart,
    create_selected_cargo_revenue_chart,
)


def create_summary() -> CargoSolutionSummary:
    return CargoSolutionSummary(
        status="OPTIMAL",
        aircraft_id="TEST-001",
        selected_items=2,
        total_revenue_usd=12000,
        total_weight_kg=1000,
        total_volume_m3=5.0,
        weight_utilization_pct=50.0,
        volume_utilization_pct=50.0,
    )


def create_result() -> CargoOptimizationResult:
    selected_cargo = pd.DataFrame(
        {
            "cargo_id": ["C001", "C002"],
            "description": [
                "Medicamentos",
                "Electrónica",
            ],
            "weight_kg": [400, 600],
            "volume_m3": [2.0, 3.0],
            "revenue_usd": [5000, 7000],
            "priority": [3, 2],
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


def test_create_capacity_utilization_chart(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "capacity.png"

    result_path = create_capacity_utilization_chart(
        create_summary(),
        output_path,
    )

    assert result_path.exists()
    assert result_path.stat().st_size > 0


def test_create_selected_cargo_revenue_chart(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "revenue.png"

    result_path = create_selected_cargo_revenue_chart(
        create_result(),
        output_path,
    )

    assert result_path.exists()
    assert result_path.stat().st_size > 0


def test_revenue_chart_rejects_empty_selection(
    tmp_path: Path,
) -> None:
    empty_result = CargoOptimizationResult(
        status="OPTIMAL",
        objective_value=0,
        selected_cargo=pd.DataFrame(),
        total_weight_kg=0,
        total_volume_m3=0,
        total_revenue_usd=0,
    )

    with pytest.raises(
        ValueError,
        match="No existen cargas seleccionadas",
    ):
        create_selected_cargo_revenue_chart(
            empty_result,
            tmp_path / "empty.png",
        )