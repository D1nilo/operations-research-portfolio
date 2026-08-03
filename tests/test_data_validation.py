import pandas as pd
import pytest

from airline_cargo_optimization.data_validation import (
    validate_cargo_data,
)


def create_valid_cargo_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "cargo_id": ["C001", "C002"],
            "description": [
                "Medicamentos",
                "Equipamiento médico",
            ],
            "weight_kg": [450, 800],
            "volume_m3": [2.5, 4.0],
            "revenue_usd": [5200, 6800],
            "priority": [3, 2],
        }
    )


def test_validate_cargo_data_accepts_valid_data() -> None:
    cargo_data = create_valid_cargo_data()

    validate_cargo_data(cargo_data)


def test_validate_cargo_data_rejects_empty_data() -> None:
    cargo_data = pd.DataFrame()

    with pytest.raises(
        ValueError,
        match="no contiene registros",
    ):
        validate_cargo_data(cargo_data)


def test_validate_cargo_data_rejects_duplicate_ids() -> None:
    cargo_data = create_valid_cargo_data()
    cargo_data.loc[1, "cargo_id"] = "C001"

    with pytest.raises(
        ValueError,
        match="duplicados",
    ):
        validate_cargo_data(cargo_data)


def test_validate_cargo_data_rejects_negative_weight() -> None:
    cargo_data = create_valid_cargo_data()
    cargo_data.loc[0, "weight_kg"] = -100

    with pytest.raises(
        ValueError,
        match="peso",
    ):
        validate_cargo_data(cargo_data)


def test_validate_cargo_data_rejects_invalid_priority() -> None:
    cargo_data = create_valid_cargo_data()
    cargo_data.loc[0, "priority"] = 5

    with pytest.raises(
        ValueError,
        match="prioridades",
    ):
        validate_cargo_data(cargo_data)