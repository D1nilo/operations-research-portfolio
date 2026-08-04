from dataclasses import dataclass

import pandas as pd
from ortools.linear_solver import pywraplp

from airline_cargo_optimization.model import CargoOptimizationModel


@dataclass(frozen=True)
class CargoOptimizationResult:
    status: str
    objective_value: float
    selected_cargo: pd.DataFrame
    total_weight_kg: float
    total_volume_m3: float
    total_revenue_usd: float
    wall_time_ms: int
    iterations: int
    nodes: int
    variable_count: int
    constraint_count: int


def solve_cargo_model(
    model: CargoOptimizationModel,
    cargo_data: pd.DataFrame,
) -> CargoOptimizationResult:
    status_code = model.solver.Solve()

    status_mapping = {
        pywraplp.Solver.OPTIMAL: "OPTIMAL",
        pywraplp.Solver.FEASIBLE: "FEASIBLE",
        pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
        pywraplp.Solver.UNBOUNDED: "UNBOUNDED",
        pywraplp.Solver.ABNORMAL: "ABNORMAL",
        pywraplp.Solver.NOT_SOLVED: "NOT_SOLVED",
    }

    status = status_mapping.get(status_code, "UNKNOWN")

    if status_code not in {
        pywraplp.Solver.OPTIMAL,
        pywraplp.Solver.FEASIBLE,
    }:
        raise RuntimeError(
            f"El modelo no encontró una solución válida. Estado: {status}"
        )

    selected_ids = {
        cargo_id
        for cargo_id, variable in model.selection_variables.items()
        if variable.solution_value() > 0.5
    }

    selected_cargo = cargo_data[
        cargo_data["cargo_id"].isin(selected_ids)
    ].copy()

    return CargoOptimizationResult(
        status=status,
        objective_value=float(
            model.solver.Objective().Value()
        ),
        selected_cargo=selected_cargo,
        total_weight_kg=float(
            selected_cargo["weight_kg"].sum()
        ),
        total_volume_m3=float(
            selected_cargo["volume_m3"].sum()
        ),
        total_revenue_usd=float(
            selected_cargo["revenue_usd"].sum()
        ),
        wall_time_ms=model.solver.WallTime(),
        iterations=model.solver.Iterations(),
        nodes=model.solver.Nodes(),
        variable_count=model.solver.NumVariables(),
        constraint_count=model.solver.NumConstraints(),
    )