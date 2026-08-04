import json
from pathlib import Path

import pytest

from airline_cargo_optimization.config import (
    load_aircraft_config,
    validate_aircraft_config,
)


def create_valid_config() -> dict[str, object]:
    return {
        "aircraft_id": "B767F-001",
        "max_weight_kg": 5000,
        "max_volume_m3": 24.0,
        "minimum_priority_3_items": 2,
        "compartments": [
            {
                "compartment_id": "FORWARD",
                "description": "Compartimiento delantero",
                "max_weight_kg": 1600,
                "max_volume_m3": 8.0,
            },
            {
                "compartment_id": "MAIN",
                "description": "Compartimiento principal",
                "max_weight_kg": 2200,
                "max_volume_m3": 10.0,
            },
            {
                "compartment_id": "AFT",
                "description": "Compartimiento trasero",
                "max_weight_kg": 1200,
                "max_volume_m3": 6.0,
            },
        ],
    }


def test_validate_aircraft_config_accepts_valid_config() -> None:
    validate_aircraft_config(create_valid_config())


def test_validate_aircraft_config_rejects_missing_key() -> None:
    config = create_valid_config()
    del config["max_weight_kg"]

    with pytest.raises(
        ValueError,
        match="Faltan parámetros obligatorios",
    ):
        validate_aircraft_config(config)


def test_validate_aircraft_config_rejects_zero_weight() -> None:
    config = create_valid_config()
    config["max_weight_kg"] = 0

    with pytest.raises(
        ValueError,
        match="max_weight_kg",
    ):
        validate_aircraft_config(config)


def test_validate_aircraft_config_rejects_negative_volume() -> None:
    config = create_valid_config()
    config["max_volume_m3"] = -10

    with pytest.raises(
        ValueError,
        match="max_volume_m3",
    ):
        validate_aircraft_config(config)


def test_validate_aircraft_config_rejects_empty_aircraft_id() -> None:
    config = create_valid_config()
    config["aircraft_id"] = "   "

    with pytest.raises(
        ValueError,
        match="identificador de la aeronave",
    ):
        validate_aircraft_config(config)


def test_validate_aircraft_config_rejects_empty_compartments() -> None:
    config = create_valid_config()
    config["compartments"] = []

    with pytest.raises(
        ValueError,
        match="al menos un compartimiento",
    ):
        validate_aircraft_config(config)


def test_validate_aircraft_config_rejects_non_list_compartments() -> None:
    config = create_valid_config()
    config["compartments"] = {}

    with pytest.raises(
        TypeError,
        match="debe ser una lista",
    ):
        validate_aircraft_config(config)


def test_validate_aircraft_config_rejects_duplicate_compartment_ids() -> None:
    config = create_valid_config()

    compartments = config["compartments"]

    assert isinstance(compartments, list)

    compartments[1]["compartment_id"] = "FORWARD"

    with pytest.raises(
        ValueError,
        match="duplicados",
    ):
        validate_aircraft_config(config)


def test_validate_aircraft_config_rejects_empty_compartment_id() -> None:
    config = create_valid_config()

    compartments = config["compartments"]

    assert isinstance(compartments, list)

    compartments[0]["compartment_id"] = "   "

    with pytest.raises(
        ValueError,
        match="identificador del compartimiento",
    ):
        validate_aircraft_config(config)


def test_validate_aircraft_config_rejects_empty_compartment_description() -> None:
    config = create_valid_config()

    compartments = config["compartments"]

    assert isinstance(compartments, list)

    compartments[0]["description"] = ""

    with pytest.raises(
        ValueError,
        match="debe incluir una descripción",
    ):
        validate_aircraft_config(config)


def test_validate_aircraft_config_rejects_invalid_compartment_weight() -> None:
    config = create_valid_config()

    compartments = config["compartments"]

    assert isinstance(compartments, list)

    compartments[0]["max_weight_kg"] = 0

    with pytest.raises(
        ValueError,
        match="FORWARD.max_weight_kg",
    ):
        validate_aircraft_config(config)


def test_validate_aircraft_config_rejects_invalid_compartment_volume() -> None:
    config = create_valid_config()

    compartments = config["compartments"]

    assert isinstance(compartments, list)

    compartments[0]["max_volume_m3"] = -1

    with pytest.raises(
        ValueError,
        match="FORWARD.max_volume_m3",
    ):
        validate_aircraft_config(config)


def test_validate_aircraft_config_rejects_weight_total_mismatch() -> None:
    config = create_valid_config()

    compartments = config["compartments"]

    assert isinstance(compartments, list)

    compartments[0]["max_weight_kg"] = 1500

    with pytest.raises(
        ValueError,
        match="capacidades de peso",
    ):
        validate_aircraft_config(config)


def test_validate_aircraft_config_rejects_volume_total_mismatch() -> None:
    config = create_valid_config()

    compartments = config["compartments"]

    assert isinstance(compartments, list)

    compartments[0]["max_volume_m3"] = 7.0

    with pytest.raises(
        ValueError,
        match="capacidades de volumen",
    ):
        validate_aircraft_config(config)


def test_load_aircraft_config_reads_json(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "aircraft_config.json"

    config_path.write_text(
        json.dumps(create_valid_config()),
        encoding="utf-8",
    )

    config = load_aircraft_config(config_path)

    assert config["aircraft_id"] == "B767F-001"
    assert config["max_weight_kg"] == 5000
    assert config["max_volume_m3"] == 24.0
    assert len(config["compartments"]) == 3
