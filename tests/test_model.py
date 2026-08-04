import pandas as pd
from ortools.linear_solver import pywraplp

from airline_cargo_optimization.model import build_cargo_model


def create_cargo_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "cargo_id": ["C001", "C002", "C003"],
            "description": [
                "Medicamentos",
                "Electrónica",
                "Equipamiento médico",
            ],
            "weight_kg": [400, 600, 900],
            "volume_m3": [2.0, 3.0, 5.0],
            "revenue_usd": [5000, 7000, 9000],
            "priority": [3, 2, 3],
        }
    )


def create_aircraft_config() -> dict[str, object]:
    return {
        "aircraft_id": "TEST-001",
        "max_weight_kg": 1000,
        "max_volume_m3": 6.0,
        "minimum_priority_3_items": 1,
        "compartments": [
            {
                "compartment_id": "FORWARD",
                "description": "Compartimiento delantero",
                "max_weight_kg": 600,
                "max_volume_m3": 3.0,
            },
            {
                "compartment_id": "AFT",
                "description": "Compartimiento trasero",
                "max_weight_kg": 400,
                "max_volume_m3": 3.0,
            },
        ],
    }


def test_build_cargo_model_creates_expected_variables() -> None:
    cargo_data = create_cargo_data()

    model = build_cargo_model(
        cargo_data,
        create_aircraft_config(),
    )

    assert len(model.selection_variables) == 3
    assert len(model.assignment_variables) == 6

    assert set(model.selection_variables) == {
        "C001",
        "C002",
        "C003",
    }

    assert set(model.assignment_variables) == {
        ("C001", "FORWARD"),
        ("C001", "AFT"),
        ("C002", "FORWARD"),
        ("C002", "AFT"),
        ("C003", "FORWARD"),
        ("C003", "AFT"),
    }


def test_build_cargo_model_creates_expected_constraints() -> None:
    model = build_cargo_model(
        create_cargo_data(),
        create_aircraft_config(),
    )

    assert model.solver.NumConstraints() == 10


def test_build_cargo_model_uses_binary_variables() -> None:
    model = build_cargo_model(
        create_cargo_data(),
        create_aircraft_config(),
    )

    all_variables = [
        *model.selection_variables.values(),
        *model.assignment_variables.values(),
    ]

    for variable in all_variables:
        assert variable.integer()
        assert variable.lb() == 0
        assert variable.ub() == 1


def test_selected_cargo_is_assigned_to_one_compartment() -> None:
    cargo_data = create_cargo_data()

    model = build_cargo_model(
        cargo_data,
        create_aircraft_config(),
    )

    status = model.solver.Solve()

    assert status == pywraplp.Solver.OPTIMAL

    for cargo_id, selection_variable in model.selection_variables.items():
        assigned_compartments = sum(
            variable.solution_value()
            for (
                assigned_cargo_id,
                _,
            ), variable in model.assignment_variables.items()
            if assigned_cargo_id == cargo_id
        )

        assert assigned_compartments == (selection_variable.solution_value())


def test_compartment_weight_capacities_are_respected() -> None:
    cargo_data = create_cargo_data()
    config = create_aircraft_config()

    model = build_cargo_model(
        cargo_data,
        config,
    )

    status = model.solver.Solve()

    assert status == pywraplp.Solver.OPTIMAL

    cargo_weights = cargo_data.set_index("cargo_id")["weight_kg"].to_dict()

    compartments = config["compartments"]

    assert isinstance(compartments, list)

    for compartment in compartments:
        compartment_id = compartment["compartment_id"]
        max_weight = compartment["max_weight_kg"]

        assigned_weight = sum(
            cargo_weights[cargo_id]
            * model.assignment_variables[(cargo_id, compartment_id)].solution_value()
            for cargo_id in cargo_weights
        )

        assert assigned_weight <= max_weight


def test_compartment_volume_capacities_are_respected() -> None:
    cargo_data = create_cargo_data()
    config = create_aircraft_config()

    model = build_cargo_model(
        cargo_data,
        config,
    )

    status = model.solver.Solve()

    assert status == pywraplp.Solver.OPTIMAL

    cargo_volumes = cargo_data.set_index("cargo_id")["volume_m3"].to_dict()

    compartments = config["compartments"]

    assert isinstance(compartments, list)

    for compartment in compartments:
        compartment_id = compartment["compartment_id"]
        max_volume = compartment["max_volume_m3"]

        assigned_volume = sum(
            cargo_volumes[cargo_id]
            * model.assignment_variables[(cargo_id, compartment_id)].solution_value()
            for cargo_id in cargo_volumes
        )

        assert assigned_volume <= max_volume
