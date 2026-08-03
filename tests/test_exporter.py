import json
from pathlib import Path

import pandas as pd

from airline_cargo_optimization.exporter import (
    export_selected_cargo_csv,
    export_solution_summary_json,
)
from airline_cargo_optimization.results import CargoSolutionSummary
from airline_cargo_optimization.solver import CargoOptimizationResult


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


def test_export_selected_cargo_csv(tmp_path: Path) -> None:
    output_path = tmp_path / "selected_cargo.csv"

    result_path = export_selected_cargo_csv(
        create_result(),
        output_path,
    )

    exported_data = pd.read_csv(result_path)

    assert result_path.exists()
    assert len(exported_data) == 2
    assert list(exported_data["cargo_id"]) == [
        "C001",
        "C002",
    ]


def test_export_solution_summary_json(tmp_path: Path) -> None:
    output_path = tmp_path / "summary.json"

    result_path = export_solution_summary_json(
        create_summary(),
        output_path,
    )

    with result_path.open(encoding="utf-8") as file:
        exported_summary = json.load(file)

    assert result_path.exists()
    assert exported_summary["status"] == "OPTIMAL"
    assert exported_summary["aircraft_id"] == "TEST-001"
    assert exported_summary["selected_items"] == 2