import pandas as pd
import pytest

from airline_cargo_optimization.model import build_cargo_model
from airline_cargo_optimization.solver import solve_cargo_model


def create_cargo_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "cargo_id": ["C001", "C002", "C003"],
            "description": [
                "Medicamentos",
                "Baterías de litio",
                "Equipamiento médico",
            ],
            "weight_kg": [400, 350, 600],
            "volume_m3": [2.0, 1.8, 3.0],
            "revenue_usd": [5000, 6500, 7000],
            "priority": [3, 3, 2],
            "is_hazardous": [False, True, False],
            "hazard_class": ["", "CLASS_9", ""],
        }
    )


def create_aircraft_config() -> dict[str, object]:
    return {
        "aircraft_id": "TEST-001",
        "max_weight_kg": 1500,
        "max_volume_m3": 8.0,
        "minimum_priority_3_items": 1,
        "compartments": [
            {
                "compartment_id": "FORWARD",
                "description": "Compartimiento delantero",
                "max_weight_kg": 500,
                "max_volume_m3": 3.0,
                "allows_hazardous": False,
            },
            {
                "compartment_id": "MAIN",
                "description": "Compartimiento principal",
                "max_weight_kg": 700,
                "max_volume_m3": 3.0,
                "allows_hazardous": True,
            },
            {
                "compartment_id": "AFT",
                "description": "Compartimiento trasero",
                "max_weight_kg": 300,
                "max_volume_m3": 2.0,
                "allows_hazardous": False,
            },
        ],
    }


def test_solver_returns_optimal_solution() -> None:
    cargo_data = create_cargo_data()

    model = build_cargo_model(
        cargo_data,
        create_aircraft_config(),
    )

    result = solve_cargo_model(
        model,
        cargo_data,
    )

    assert result.status == "OPTIMAL"
    assert result.total_weight_kg <= 1500
    assert result.total_volume_m3 <= 8.0


def test_solver_maximizes_revenue() -> None:
    cargo_data = create_cargo_data()

    model = build_cargo_model(
        cargo_data,
        create_aircraft_config(),
    )

    result = solve_cargo_model(
        model,
        cargo_data,
    )

    assert result.total_revenue_usd == 12000

    assert set(result.selected_cargo["cargo_id"]) == {
        "C001",
        "C003",
    }


def test_solver_exposes_compartment_assignment() -> None:
    cargo_data = create_cargo_data()
    config = create_aircraft_config()

    model = build_cargo_model(
        cargo_data,
        config,
    )

    result = solve_cargo_model(
        model,
        cargo_data,
    )

    assert "compartment_id" in result.selected_cargo.columns
    assert result.selected_cargo["compartment_id"].notna().all()

    valid_compartments = {
        compartment["compartment_id"] for compartment in config["compartments"]
    }

    assert set(result.selected_cargo["compartment_id"]).issubset(valid_compartments)


def test_each_selected_cargo_has_one_compartment() -> None:
    cargo_data = create_cargo_data()

    model = build_cargo_model(
        cargo_data,
        create_aircraft_config(),
    )

    result = solve_cargo_model(
        model,
        cargo_data,
    )

    assignment_counts = result.selected_cargo.groupby("cargo_id")[
        "compartment_id"
    ].count()

    assert assignment_counts.eq(1).all()


def test_hazardous_cargo_uses_authorized_compartment_when_selected() -> None:
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

    result = solve_cargo_model(
        model,
        cargo_data,
    )

    hazardous_result = result.selected_cargo[
        result.selected_cargo["cargo_id"] == hazardous_cargo_id
    ]

    assert len(hazardous_result) == 1
    assert hazardous_result.iloc[0]["compartment_id"] == "MAIN"


def test_solver_rejects_infeasible_model() -> None:
    cargo_data = create_cargo_data()

    config = create_aircraft_config()
    config["max_weight_kg"] = 100
    config["minimum_priority_3_items"] = 2

    model = build_cargo_model(
        cargo_data,
        config,
    )

    with pytest.raises(
        RuntimeError,
        match="INFEASIBLE",
    ):
        solve_cargo_model(
            model,
            cargo_data,
        )


def test_solver_returns_technical_metrics() -> None:
    cargo_data = create_cargo_data()

    model = build_cargo_model(
        cargo_data,
        create_aircraft_config(),
    )

    result = solve_cargo_model(
        model,
        cargo_data,
    )

    assert result.wall_time_ms >= 0
    assert result.iterations >= 0
    assert result.nodes >= 0
    assert result.variable_count == 12
    assert result.constraint_count == 14


def test_solver_objective_matches_total_revenue() -> None:
    cargo_data = create_cargo_data()

    model = build_cargo_model(
        cargo_data,
        create_aircraft_config(),
    )

    result = solve_cargo_model(
        model,
        cargo_data,
    )

    assert result.objective_value == pytest.approx(result.total_revenue_usd)
