import json
from pathlib import Path
from typing import Any


REQUIRED_CONFIG_KEYS = {
    "aircraft_id",
    "max_weight_kg",
    "max_volume_m3",
    "minimum_priority_3_items",
}


def load_aircraft_config(
    file_path: str | Path,
) -> dict[str, Any]:
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"No existe el archivo de configuración: {path}")

    with path.open(encoding="utf-8") as file:
        config = json.load(file)

    validate_aircraft_config(config)

    return config


def validate_aircraft_config(
    config: dict[str, Any],
) -> None:
    missing_keys = REQUIRED_CONFIG_KEYS.difference(config)

    if missing_keys:
        raise ValueError(
            "Faltan parámetros obligatorios en la configuración: "
            f"{sorted(missing_keys)}"
        )

    aircraft_id = config["aircraft_id"]

    if not isinstance(aircraft_id, str) or not aircraft_id.strip():
        raise ValueError("El identificador de la aeronave no puede estar vacío.")

    numeric_keys = {
        "max_weight_kg",
        "max_volume_m3",
        "minimum_priority_3_items",
    }

    for key in numeric_keys:
        value = config[key]

        if not isinstance(value, int | float):
            raise TypeError(f"El parámetro '{key}' debe ser numérico.")

    if config["max_weight_kg"] <= 0:
        raise ValueError("La capacidad máxima de peso debe ser mayor que cero.")

    if config["max_volume_m3"] <= 0:
        raise ValueError("La capacidad máxima de volumen debe ser mayor que cero.")

    minimum_priority = config["minimum_priority_3_items"]

    if not isinstance(minimum_priority, int):
        raise TypeError(
            "La cantidad mínima de cargas prioritarias debe ser un número entero."
        )

    if minimum_priority < 0:
        raise ValueError(
            "La cantidad mínima de cargas prioritarias no puede ser negativa."
        )
