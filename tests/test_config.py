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
        match="peso",
    ):
        validate_aircraft_config(config)


def test_validate_aircraft_config_rejects_negative_volume() -> None:
    config = create_valid_config()
    config["max_volume_m3"] = -10

    with pytest.raises(
        ValueError,
        match="volumen",
    ):
        validate_aircraft_config(config)


def test_validate_aircraft_config_rejects_empty_aircraft_id() -> None:
    config = create_valid_config()
    config["aircraft_id"] = "   "

    with pytest.raises(
        ValueError,
        match="identificador",
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
