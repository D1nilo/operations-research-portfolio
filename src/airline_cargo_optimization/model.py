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
        raise RuntimeError(
            "No fue posible inicializar el solver SCIP."
        )

    compartments = aircraft_config["compartments"]

    selection_variables = {
        row.cargo_id: solver.BoolVar(
            f"select_{row.cargo_id}"
        )
        for row in cargo_data.itertuples(index=False)
    }

    assignment_variables = {
        (
            row.cargo_id,
            compartment["compartment_id"],
        ): solver.BoolVar(
            "assign_"
            f"{row.cargo_id}_"
            f"{compartment['compartment_id']}"
        )
        for row in cargo_data.itertuples(index=False)
        for compartment in compartments
    }

    add_assignment_link_constraints(
        solver,
        cargo_data,
        compartments,
        selection_variables,
        assignment_variables,
    )

    add_aircraft_capacity_constraints(
        solver,
        cargo_data,
        aircraft_config,
        selection_variables,
    )

    add_compartment_capacity_constraints(
        solver,
        cargo_data,
        compartments,
        assignment_variables,
    )

    add_hazardous_cargo_constraints(
        solver,
        cargo_data,
        compartments,
        assignment_variables,
    )

    add_cold_chain_constraints(
        solver,
        cargo_data,
        compartments,
        assignment_variables,
    )

    add_incompatibility_constraints(
        solver,
        aircraft_config,
        compartments,
        assignment_variables,
    )

    add_route_compatibility_constraints(
        solver,
        cargo_data,
        aircraft_config,
        selection_variables,
    )

    add_priority_constraint(
        solver,
        cargo_data,
        aircraft_config,
        selection_variables,
    )

    solver.Maximize(
        sum(
            row.revenue_usd
            * selection_variables[row.cargo_id]
            for row in cargo_data.itertuples(index=False)
        )
    )

    return CargoOptimizationModel(
        solver=solver,
        selection_variables=selection_variables,
        assignment_variables=assignment_variables,
    )


def add_assignment_link_constraints(
    solver: pywraplp.Solver,
    cargo_data: pd.DataFrame,
    compartments: list[dict[str, Any]],
    selection_variables: dict[
        str,
        pywraplp.Variable,
    ],
    assignment_variables: dict[
        tuple[str, str],
        pywraplp.Variable,
    ],
) -> None:
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


def add_aircraft_capacity_constraints(
    solver: pywraplp.Solver,
    cargo_data: pd.DataFrame,
    aircraft_config: dict[str, Any],
    selection_variables: dict[
        str,
        pywraplp.Variable,
    ],
) -> None:
    solver.Add(
        sum(
            row.weight_kg
            * selection_variables[row.cargo_id]
            for row in cargo_data.itertuples(index=False)
        )
        <= aircraft_config["max_weight_kg"],
        "max_aircraft_weight_constraint",
    )

    solver.Add(
        sum(
            row.volume_m3
            * selection_variables[row.cargo_id]
            for row in cargo_data.itertuples(index=False)
        )
        <= aircraft_config["max_volume_m3"],
        "max_aircraft_volume_constraint",
    )


def add_compartment_capacity_constraints(
    solver: pywraplp.Solver,
    cargo_data: pd.DataFrame,
    compartments: list[dict[str, Any]],
    assignment_variables: dict[
        tuple[str, str],
        pywraplp.Variable,
    ],
) -> None:
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


def add_hazardous_cargo_constraints(
    solver: pywraplp.Solver,
    cargo_data: pd.DataFrame,
    compartments: list[dict[str, Any]],
    assignment_variables: dict[
        tuple[str, str],
        pywraplp.Variable,
    ],
) -> None:
    hazardous_cargo = cargo_data[
        cargo_data["is_hazardous"]
    ]

    unauthorized_compartments = [
        compartment
        for compartment in compartments
        if not compartment["allows_hazardous"]
    ]

    for row in hazardous_cargo.itertuples(index=False):
        for compartment in unauthorized_compartments:
            compartment_id = compartment["compartment_id"]

            solver.Add(
                assignment_variables[
                    (
                        row.cargo_id,
                        compartment_id,
                    )
                ]
                == 0,
                "hazardous_restriction_"
                f"{row.cargo_id}_"
                f"{compartment_id}",
            )


def add_cold_chain_constraints(
    solver: pywraplp.Solver,
    cargo_data: pd.DataFrame,
    compartments: list[dict[str, Any]],
    assignment_variables: dict[
        tuple[str, str],
        pywraplp.Variable,
    ],
) -> None:
    cold_chain_cargo = cargo_data[
        cargo_data["requires_cold_chain"]
    ]

    unsupported_compartments = [
        compartment
        for compartment in compartments
        if not compartment["supports_cold_chain"]
    ]

    for row in cold_chain_cargo.itertuples(index=False):
        for compartment in unsupported_compartments:
            compartment_id = compartment["compartment_id"]

            solver.Add(
                assignment_variables[
                    (
                        row.cargo_id,
                        compartment_id,
                    )
                ]
                == 0,
                "cold_chain_restriction_"
                f"{row.cargo_id}_"
                f"{compartment_id}",
            )


def add_incompatibility_constraints(
    solver: pywraplp.Solver,
    aircraft_config: dict[str, Any],
    compartments: list[dict[str, Any]],
    assignment_variables: dict[
        tuple[str, str],
        pywraplp.Variable,
    ],
) -> None:
    incompatible_pairs = aircraft_config[
        "incompatible_cargo_pairs"
    ]

    for pair in incompatible_pairs:
        cargo_id_1 = str(
            pair["cargo_id_1"]
        ).strip().upper()

        cargo_id_2 = str(
            pair["cargo_id_2"]
        ).strip().upper()

        for compartment in compartments:
            compartment_id = compartment["compartment_id"]

            solver.Add(
                assignment_variables[
                    (
                        cargo_id_1,
                        compartment_id,
                    )
                ]
                + assignment_variables[
                    (
                        cargo_id_2,
                        compartment_id,
                    )
                ]
                <= 1,
                "incompatibility_"
                f"{cargo_id_1}_"
                f"{cargo_id_2}_"
                f"{compartment_id}",
            )


def add_route_compatibility_constraints(
    solver: pywraplp.Solver,
    cargo_data: pd.DataFrame,
    aircraft_config: dict[str, Any],
    selection_variables: dict[
        str,
        pywraplp.Variable,
    ],
) -> None:
    route_airports = {
        str(stop["airport_code"])
        .strip()
        .upper()
        for stop in aircraft_config["route"]
    }

    for row in cargo_data.itertuples(index=False):
        destination = str(
            row.destination
        ).strip().upper()

        if destination not in route_airports:
            solver.Add(
                selection_variables[row.cargo_id] == 0,
                f"out_of_route_{row.cargo_id}_{destination}",
            )


def add_priority_constraint(
    solver: pywraplp.Solver,
    cargo_data: pd.DataFrame,
    aircraft_config: dict[str, Any],
    selection_variables: dict[
        str,
        pywraplp.Variable,
    ],
) -> None:
    high_priority_cargo = cargo_data[
        cargo_data["priority"] == 3
    ]

    solver.Add(
        sum(
            selection_variables[row.cargo_id]
            for row in high_priority_cargo.itertuples(
                index=False
            )
        )
        >= aircraft_config[
            "minimum_priority_3_items"
        ],
        "minimum_high_priority_constraint",
    )