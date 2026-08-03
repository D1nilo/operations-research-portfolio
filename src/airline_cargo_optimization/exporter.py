import json
from dataclasses import asdict
from pathlib import Path

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
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            asdict(summary),
            file,
            ensure_ascii=False,
            indent=2,
        )

    return path
