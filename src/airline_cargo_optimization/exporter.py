import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from airline_cargo_optimization.results import CargoSolutionSummary
from airline_cargo_optimization.solver import CargoOptimizationResult


def export_selected_cargo_csv(
    result: CargoOptimizationResult,
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    result.selected_cargo.to_csv(
        path,
        index=False,
        encoding="utf-8",
    )

    return path


def export_solution_summary_json(
    summary: CargoSolutionSummary,
    result: CargoOptimizationResult,
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    cargo_assignments = result.selected_cargo[["cargo_id", "compartment_id"]].to_dict(
        orient="records"
    )

    payload: dict[str, Any] = {
        **asdict(summary),
        "solver_metrics": {
            "objective_value": result.objective_value,
            "wall_time_ms": result.wall_time_ms,
            "iterations": result.iterations,
            "nodes": result.nodes,
            "variable_count": result.variable_count,
            "constraint_count": result.constraint_count,
        },
        "cargo_assignments": cargo_assignments,
    }

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            payload,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return path
