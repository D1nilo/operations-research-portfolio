import pandas as pd

from airline_cargo_optimization.model import (
    build_cargo_model,
)


def create_cargo_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "cargo_id": ["C001", "C002", "C003"],
            "description": [
                "Medicamentos",
                "Electrónica",
                "Equipamiento médico",
            ],
            "weight_kg": [450, 800, 1100],
            "volume_m3": [2.5, 4.0, 5.0],
            "revenue_usd": [5200, 6800, 8800],
            "priority": [3, 2, 3],
        }
    )


def create_aircraft_config() -> dict[str, object]:
    return {
        "aircraft_id": "TEST-001",
        "max_weight_kg": 1500,
        "max_volume_m3": 10.0,
        "minimum_priority_3_items": 1,
    }


def test_build_cargo_model_creates_one_variable_per_cargo() -> None:
    cargo_data = create_cargo_data()

    model = build_cargo_model(
        cargo_data,
        create_aircraft_config(),
    )

    assert len(model.selection_variables) == len(cargo_data)

    assert set(model.selection_variables) == {
        "C001",
        "C002",
        "C003",
    }


def test_build_cargo_model_creates_expected_constraints() -> None:
    model = build_cargo_model(
        create_cargo_data(),
        create_aircraft_config(),
    )

    assert model.solver.NumConstraints() == 3


def test_build_cargo_model_uses_binary_variables() -> None:
    model = build_cargo_model(
        create_cargo_data(),
        create_aircraft_config(),
    )

    for variable in model.selection_variables.values():
        assert variable.integer()
        assert variable.lb() == 0
        assert variable.ub() == 1
