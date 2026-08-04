from dataclasses import dataclass
from typing import Any

import pandas as pd
from ortools.linear_solver import pywraplp


@dataclass(frozen=True)
class CargoOptimizationModel:
    solver: pywraplp.Solver
    selection_variables: dict[str, pywraplp.Variable]
    assignment_variables: dict[
        tuple[str, str],
        pywraplp.Variable,
    ]


def build_cargo_model(
    cargo_data: pd.DataFrame,
    aircraft_config: dict[str, Any],
) -> CargoOptimizationModel:
    solver = pywraplp.Solver.CreateSolver("SCIP")

    if solver is None:
        raise RuntimeError("No fue posible inicializar el solver SCIP.")

    compartments = aircraft_config["compartments"]

    selection_variables = {
        row.cargo_id: solver.BoolVar(f"select_{row.cargo_id}")
        for row in cargo_data.itertuples(index=False)
    }

    assignment_variables = {
        (
            row.cargo_id,
            compartment["compartment_id"],
        ): solver.BoolVar(f"assign_{row.cargo_id}_{compartment['compartment_id']}")
        for row in cargo_data.itertuples(index=False)
        for compartment in compartments
    }

    for row in cargo_data.itertuples(index=False):
        solver.Add(
            sum(
                assignment_variables[
                    (
                        row.cargo_id,
                        compartment["compartment_id"],
                    )
                ]
                for compartment in compartments
            )
            == selection_variables[row.cargo_id],
            f"assignment_link_{row.cargo_id}",
        )

    solver.Add(
        sum(
            row.weight_kg * selection_variables[row.cargo_id]
            for row in cargo_data.itertuples(index=False)
        )
        <= aircraft_config["max_weight_kg"],
        "max_aircraft_weight_constraint",
    )

    solver.Add(
        sum(
            row.volume_m3 * selection_variables[row.cargo_id]
            for row in cargo_data.itertuples(index=False)
        )
        <= aircraft_config["max_volume_m3"],
        "max_aircraft_volume_constraint",
    )

    for compartment in compartments:
        compartment_id = compartment["compartment_id"]

        solver.Add(
            sum(
                row.weight_kg
                * assignment_variables[
                    (
                        row.cargo_id,
                        compartment_id,
                    )
                ]
                for row in cargo_data.itertuples(index=False)
            )
            <= compartment["max_weight_kg"],
            f"max_weight_{compartment_id}",
        )

        solver.Add(
            sum(
                row.volume_m3
                * assignment_variables[
                    (
                        row.cargo_id,
                        compartment_id,
                    )
                ]
                for row in cargo_data.itertuples(index=False)
            )
            <= compartment["max_volume_m3"],
            f"max_volume_{compartment_id}",
        )

    hazardous_cargo = cargo_data[cargo_data["is_hazardous"]]

    unauthorized_hazardous_compartments = [
        compartment
        for compartment in compartments
        if not compartment["allows_hazardous"]
    ]

    for row in hazardous_cargo.itertuples(index=False):
        for compartment in unauthorized_hazardous_compartments:
            compartment_id = compartment["compartment_id"]

            solver.Add(
                assignment_variables[
                    (
                        row.cargo_id,
                        compartment_id,
                    )
                ]
                == 0,
                f"hazardous_restriction_{row.cargo_id}_{compartment_id}",
            )

    cold_chain_cargo = cargo_data[cargo_data["requires_cold_chain"]]

    unsupported_cold_chain_compartments = [
        compartment
        for compartment in compartments
        if not compartment["supports_cold_chain"]
    ]

    for row in cold_chain_cargo.itertuples(index=False):
        for compartment in unsupported_cold_chain_compartments:
            compartment_id = compartment["compartment_id"]

            solver.Add(
                assignment_variables[
                    (
                        row.cargo_id,
                        compartment_id,
                    )
                ]
                == 0,
                f"cold_chain_restriction_{row.cargo_id}_{compartment_id}",
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
        assignment_variables=assignment_variables,
    )
