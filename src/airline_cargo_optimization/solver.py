from typing import Any

import pandas as pd
from ortools.linear_solver import pywraplp


def solve_cargo_model(
    solver: pywraplp.Solver,
    selection_variables: dict[str, pywraplp.Variable],
    cargo_data: pd.DataFrame,
) -> dict[str, Any]:
    status = solver.Solve()

    valid_statuses = {
        pywraplp.Solver.OPTIMAL,
        pywraplp.Solver.FEASIBLE,
    }

    if status not in valid_statuses:
        raise RuntimeError(
            f"El modelo no encontró una solución factible. Estado: {status}"
        )

    selected_ids = {
        cargo_id
        for cargo_id, variable in selection_variables.items()
        if variable.solution_value() > 0.5
    }

    selected_cargo = cargo_data[
        cargo_data["cargo_id"].isin(selected_ids)
    ].copy()

    return {
        "status": "OPTIMAL"
        if status == pywraplp.Solver.OPTIMAL
        else "FEASIBLE",
        "objective_value": solver.Objective().Value(),
        "selected_cargo": selected_cargo,
        "total_weight_kg": selected_cargo["weight_kg"].sum(),
        "total_volume_m3": selected_cargo["volume_m3"].sum(),
        "total_revenue_usd": selected_cargo["revenue_usd"].sum(),
    }