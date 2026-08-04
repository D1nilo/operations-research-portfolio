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
    assert result.total_weight_kg <= 1000
    assert result.total_volume_m3 <= 6.0


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
        "C002",
    }


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
    assert result.variable_count == 9
    assert result.constraint_count == 8


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
