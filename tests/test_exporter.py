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
            "compartment_id": [
                "AFT",
                "FORWARD",
            ],
        }
    )

    return CargoOptimizationResult(
        status="OPTIMAL",
        objective_value=12000,
        selected_cargo=selected_cargo,
        total_weight_kg=1000,
        total_volume_m3=5.0,
        total_revenue_usd=12000,
        wall_time_ms=10,
        iterations=0,
        nodes=1,
        variable_count=9,
        constraint_count=10,
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
    assert "compartment_id" in exported_data.columns

    assert list(exported_data["cargo_id"]) == [
        "C001",
        "C002",
    ]

    assert list(exported_data["compartment_id"]) == [
        "AFT",
        "FORWARD",
    ]


def test_export_solution_summary_json(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "summary.json"

    result_path = export_solution_summary_json(
        create_summary(),
        create_result(),
        output_path,
    )

    with result_path.open(encoding="utf-8") as file:
        exported_summary = json.load(file)

    assert result_path.exists()
    assert exported_summary["status"] == "OPTIMAL"
    assert exported_summary["aircraft_id"] == "TEST-001"
    assert exported_summary["selected_items"] == 2
    assert exported_summary["total_revenue_usd"] == 12000

    solver_metrics = exported_summary["solver_metrics"]

    assert solver_metrics["objective_value"] == 12000
    assert solver_metrics["wall_time_ms"] == 10
    assert solver_metrics["iterations"] == 0
    assert solver_metrics["nodes"] == 1
    assert solver_metrics["variable_count"] == 9
    assert solver_metrics["constraint_count"] == 10

    cargo_assignments = exported_summary["cargo_assignments"]

    assert cargo_assignments == [
        {
            "cargo_id": "C001",
            "compartment_id": "AFT",
        },
        {
            "cargo_id": "C002",
            "compartment_id": "FORWARD",
        },
    ]
