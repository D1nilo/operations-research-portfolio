from dataclasses import dataclass
from typing import Any

import pandas as pd
from ortools.linear_solver import pywraplp


@dataclass(frozen=True)
class CargoOptimizationModel:
    solver: pywraplp.Solver
    selection_variables: dict[str, pywraplp.Variable]


def build_cargo_model(
    cargo_data: pd.DataFrame,
    aircraft_config: dict[str, Any],
) -> CargoOptimizationModel:
    solver = pywraplp.Solver.CreateSolver("SCIP")

    if solver is None:
        raise RuntimeError("No fue posible inicializar el solver SCIP.")

    selection_variables = {
        row.cargo_id: solver.BoolVar(f"select_{row.cargo_id}")
        for row in cargo_data.itertuples(index=False)
    }

    solver.Add(
        sum(
            row.weight_kg * selection_variables[row.cargo_id]
            for row in cargo_data.itertuples(index=False)
        )
        <= aircraft_config["max_weight_kg"],
        "max_weight_constraint",
    )

    solver.Add(
        sum(
            row.volume_m3 * selection_variables[row.cargo_id]
            for row in cargo_data.itertuples(index=False)
        )
        <= aircraft_config["max_volume_m3"],
        "max_volume_constraint",
    )

    high_priority_cargo = cargo_data[cargo_data["priority"] == 3]

    solver.Add(
        sum(
            selection_variables[row.cargo_id]
            for row in high_priority_cargo.itertuples(index=False)
        )
        >= aircraft_config["minimum_priority_3_items"],
        "minimum_high_priority_constraint",
    )

    solver.Maximize(
        sum(
            row.revenue_usd * selection_variables[row.cargo_id]
            for row in cargo_data.itertuples(index=False)
        )
    )

    return CargoOptimizationModel(
        solver=solver,
        selection_variables=selection_variables,
    )
