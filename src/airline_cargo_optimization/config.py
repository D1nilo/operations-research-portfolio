import json
import math
from pathlib import Path
from typing import Any

REQUIRED_CONFIG_KEYS = {
    "aircraft_id",
    "max_weight_kg",
    "max_volume_m3",
    "minimum_priority_3_items",
    "compartments",
}

REQUIRED_COMPARTMENT_KEYS = {
    "compartment_id",
    "description",
    "max_weight_kg",
    "max_volume_m3",
    "allows_hazardous",
    "supports_cold_chain",
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

    max_weight_kg = validate_positive_number(
        config["max_weight_kg"],
        "max_weight_kg",
    )

    max_volume_m3 = validate_positive_number(
        config["max_volume_m3"],
        "max_volume_m3",
    )

    minimum_priority = config["minimum_priority_3_items"]

    if isinstance(minimum_priority, bool) or not isinstance(
        minimum_priority,
        int,
    ):
        raise TypeError(
            "La cantidad mínima de cargas prioritarias debe ser un número entero."
        )

    if minimum_priority < 0:
        raise ValueError(
            "La cantidad mínima de cargas prioritarias no puede ser negativa."
        )

    validate_compartments(
        config["compartments"],
        max_weight_kg,
        max_volume_m3,
    )


def validate_compartments(
    compartments: Any,
    aircraft_max_weight_kg: float,
    aircraft_max_volume_m3: float,
) -> None:
    if not isinstance(compartments, list):
        raise TypeError("El parámetro 'compartments' debe ser una lista.")

    if not compartments:
        raise ValueError("La aeronave debe contener al menos un compartimiento.")

    compartment_ids: list[str] = []
    total_compartment_weight = 0.0
    total_compartment_volume = 0.0
    hazardous_enabled_compartments = 0
    cold_chain_enabled_compartments = 0

    for position, compartment in enumerate(
        compartments,
        start=1,
    ):
        if not isinstance(compartment, dict):
            raise TypeError(
                "Cada compartimiento debe estar representado "
                "por un objeto de configuración."
            )

        missing_keys = REQUIRED_COMPARTMENT_KEYS.difference(compartment)

        if missing_keys:
            raise ValueError(
                f"El compartimiento de la posición {position} "
                "no contiene todos los parámetros obligatorios: "
                f"{sorted(missing_keys)}"
            )

        compartment_id = compartment["compartment_id"]

        if not isinstance(compartment_id, str) or not compartment_id.strip():
            raise ValueError(
                "El identificador del compartimiento no puede estar vacío."
            )

        normalized_id = compartment_id.strip().upper()
        compartment_ids.append(normalized_id)

        description = compartment["description"]

        if not isinstance(description, str) or not description.strip():
            raise ValueError(
                f"El compartimiento '{normalized_id}' debe incluir una descripción."
            )

        compartment_weight = validate_positive_number(
            compartment["max_weight_kg"],
            f"{normalized_id}.max_weight_kg",
        )

        compartment_volume = validate_positive_number(
            compartment["max_volume_m3"],
            f"{normalized_id}.max_volume_m3",
        )

        allows_hazardous = compartment["allows_hazardous"]

        if not isinstance(allows_hazardous, bool):
            raise TypeError(
                f"El parámetro '{normalized_id}.allows_hazardous' debe ser booleano."
            )

        supports_cold_chain = compartment["supports_cold_chain"]

        if not isinstance(supports_cold_chain, bool):
            raise TypeError(
                f"El parámetro '{normalized_id}.supports_cold_chain' debe ser booleano."
            )

        if allows_hazardous:
            hazardous_enabled_compartments += 1

        if supports_cold_chain:
            cold_chain_enabled_compartments += 1

        total_compartment_weight += compartment_weight
        total_compartment_volume += compartment_volume

    duplicated_ids = {
        compartment_id
        for compartment_id in compartment_ids
        if compartment_ids.count(compartment_id) > 1
    }

    if duplicated_ids:
        raise ValueError(
            "Existen identificadores de compartimiento duplicados: "
            f"{sorted(duplicated_ids)}"
        )

    if hazardous_enabled_compartments == 0:
        raise ValueError(
            "Debe existir al menos un compartimiento autorizado "
            "para mercancías peligrosas."
        )

    if cold_chain_enabled_compartments == 0:
        raise ValueError(
            "Debe existir al menos un compartimiento con soporte para cadena de frío."
        )

    if not math.isclose(
        total_compartment_weight,
        aircraft_max_weight_kg,
        rel_tol=1e-9,
        abs_tol=1e-6,
    ):
        raise ValueError(
            "La suma de las capacidades de peso de los "
            "compartimientos no coincide con la capacidad total "
            "de la aeronave. "
            f"Compartimientos: {total_compartment_weight:.2f} kg. "
            f"Aeronave: {aircraft_max_weight_kg:.2f} kg."
        )

    if not math.isclose(
        total_compartment_volume,
        aircraft_max_volume_m3,
        rel_tol=1e-9,
        abs_tol=1e-6,
    ):
        raise ValueError(
            "La suma de las capacidades de volumen de los "
            "compartimientos no coincide con la capacidad total "
            "de la aeronave. "
            f"Compartimientos: {total_compartment_volume:.2f} m³. "
            f"Aeronave: {aircraft_max_volume_m3:.2f} m³."
        )


def validate_positive_number(
    value: Any,
    parameter_name: str,
) -> float:
    if isinstance(value, bool) or not isinstance(
        value,
        int | float,
    ):
        raise TypeError(f"El parámetro '{parameter_name}' debe ser numérico.")

    numeric_value = float(value)

    if numeric_value <= 0:
        raise ValueError(f"El parámetro '{parameter_name}' debe ser mayor que cero.")

    return numeric_value
