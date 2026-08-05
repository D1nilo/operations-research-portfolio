import pandas as pd
from ortools.linear_solver import pywraplp

from airline_cargo_optimization.model import build_cargo_model


def create_cargo_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "cargo_id": [
                "C001",
                "C002",
                "C003",
                "C004",
                "C005",
            ],
            "description": [
                "Vacunas refrigeradas",
                "Baterías de litio",
                "Equipamiento médico",
                "Alimentos perecibles",
                "Documentos urgentes",
            ],
            "weight_kg": [
                300,
                350,
                600,
                250,
                100,
            ],
            "volume_m3": [
                1.5,
                1.8,
                3.0,
                1.2,
                0.5,
            ],
            "revenue_usd": [
                7200,
                6500,
                7000,
                4000,
                1800,
            ],
            "priority": [
                3,
                3,
                2,
                2,
                3,
            ],
            "is_hazardous": [
                False,
                True,
                False,
                False,
                False,
            ],
            "hazard_class": [
                "",
                "CLASS_9",
                "",
                "",
                "",
            ],
            "requires_cold_chain": [
                True,
                False,
                False,
                False,
                False,
            ],
        }
    )


def create_aircraft_config() -> dict[str, object]:
    return {
        "aircraft_id": "TEST-001",
        "max_weight_kg": 2000,
        "max_volume_m3": 10.0,
        "minimum_priority_3_items": 1,
        "compartments": [
            {
                "compartment_id": "FORWARD",
                "description": "Compartimiento delantero",
                "max_weight_kg": 700,
                "max_volume_m3": 3.5,
                "allows_hazardous": False,
                "supports_cold_chain": True,
            },
            {
                "compartment_id": "MAIN",
                "description": "Compartimiento principal",
                "max_weight_kg": 900,
                "max_volume_m3": 4.5,
                "allows_hazardous": True,
                "supports_cold_chain": False,
            },
            {
                "compartment_id": "AFT",
                "description": "Compartimiento trasero",
                "max_weight_kg": 400,
                "max_volume_m3": 2.0,
                "allows_hazardous": False,
                "supports_cold_chain": False,
            },
        ],
        "incompatible_cargo_pairs": [
            {
                "cargo_id_1": "C002",
                "cargo_id_2": "C004",
                "reason": ("Mercancía peligrosa incompatible con alimentos perecibles"),
            }
        ],
    }


def test_build_cargo_model_creates_expected_variables() -> None:
    cargo_data = create_cargo_data()

    model = build_cargo_model(
        cargo_data,
        create_aircraft_config(),
    )

    assert len(model.selection_variables) == 5
    assert len(model.assignment_variables) == 15

    assert set(model.selection_variables) == {
        "C001",
        "C002",
        "C003",
        "C004",
        "C005",
    }


def test_build_cargo_model_creates_expected_constraints() -> None:
    model = build_cargo_model(
        create_cargo_data(),
        create_aircraft_config(),
    )

    assert model.solver.NumConstraints() == 21


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

        assert assigned_compartments == selection_variable.solution_value()


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


def test_hazardous_cargo_is_only_assigned_to_authorized_compartment() -> None:
    cargo_data = create_cargo_data()
    config = create_aircraft_config()

    model = build_cargo_model(
        cargo_data,
        config,
    )

    hazardous_cargo_id = "C002"

    model.solver.Add(
        model.selection_variables[hazardous_cargo_id] == 1,
        "force_hazardous_cargo_selection",
    )

    status = model.solver.Solve()

    assert status == pywraplp.Solver.OPTIMAL

    assigned_compartments = {
        compartment_id
        for (
            cargo_id,
            compartment_id,
        ), variable in model.assignment_variables.items()
        if cargo_id == hazardous_cargo_id and variable.solution_value() > 0.5
    }

    assert assigned_compartments == {"MAIN"}


def test_cold_chain_cargo_is_only_assigned_to_supported_compartment() -> None:
    cargo_data = create_cargo_data()
    config = create_aircraft_config()

    model = build_cargo_model(
        cargo_data,
        config,
    )

    cold_chain_cargo_id = "C001"

    model.solver.Add(
        model.selection_variables[cold_chain_cargo_id] == 1,
        "force_cold_chain_cargo_selection",
    )

    status = model.solver.Solve()

    assert status == pywraplp.Solver.OPTIMAL

    assigned_compartments = {
        compartment_id
        for (
            cargo_id,
            compartment_id,
        ), variable in model.assignment_variables.items()
        if cargo_id == cold_chain_cargo_id and variable.solution_value() > 0.5
    }

    assert assigned_compartments == {"FORWARD"}


def test_incompatible_cargo_cannot_share_compartment() -> None:
    cargo_data = create_cargo_data()
    config = create_aircraft_config()

    model = build_cargo_model(
        cargo_data,
        config,
    )

    cargo_id_1 = "C002"
    cargo_id_2 = "C004"

    model.solver.Add(
        model.selection_variables[cargo_id_1] == 1,
        "force_first_incompatible_cargo",
    )

    model.solver.Add(
        model.selection_variables[cargo_id_2] == 1,
        "force_second_incompatible_cargo",
    )

    status = model.solver.Solve()

    assert status == pywraplp.Solver.OPTIMAL

    cargo_1_compartments = {
        compartment_id
        for (
            cargo_id,
            compartment_id,
        ), variable in model.assignment_variables.items()
        if cargo_id == cargo_id_1 and variable.solution_value() > 0.5
    }

    cargo_2_compartments = {
        compartment_id
        for (
            cargo_id,
            compartment_id,
        ), variable in model.assignment_variables.items()
        if cargo_id == cargo_id_2 and variable.solution_value() > 0.5
    }

    assert len(cargo_1_compartments) == 1
    assert len(cargo_2_compartments) == 1
    assert cargo_1_compartments.isdisjoint(cargo_2_compartments)


def test_normal_cargo_can_use_general_compartments() -> None:
    cargo_data = create_cargo_data()
    config = create_aircraft_config()

    model = build_cargo_model(
        cargo_data,
        config,
    )

    status = model.solver.Solve()

    assert status == pywraplp.Solver.OPTIMAL

    selected_ids = {
        cargo_id
        for cargo_id, variable in model.selection_variables.items()
        if variable.solution_value() > 0.5
    }

    assert selected_ids
