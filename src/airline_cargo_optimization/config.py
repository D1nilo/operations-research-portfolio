import json
import math
import re
from pathlib import Path
from typing import Any


REQUIRED_CONFIG_KEYS = {
    "aircraft_id",
    "origin",
    "route",
    "max_weight_kg",
    "max_volume_m3",
    "minimum_priority_3_items",
    "compartments",
    "incompatible_cargo_pairs",
}

REQUIRED_ROUTE_STOP_KEYS = {
    "sequence",
    "airport_code",
}

REQUIRED_COMPARTMENT_KEYS = {
    "compartment_id",
    "description",
    "unloading_order",
    "max_weight_kg",
    "max_volume_m3",
    "allows_hazardous",
    "supports_cold_chain",
}

REQUIRED_INCOMPATIBILITY_KEYS = {
    "cargo_id_1",
    "cargo_id_2",
    "reason",
}

AIRPORT_CODE_PATTERN = re.compile(r"^[A-Z]{3}$")


def load_aircraft_config(
    file_path: str | Path,
) -> dict[str, Any]:
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"No existe el archivo de configuración: {path}"
        )

    with path.open(encoding="utf-8") as file:
        config = json.load(file)

    validate_aircraft_config(config)

    return config


def validate_aircraft_config(
    config: dict[str, Any],
) -> None:
    if not isinstance(config, dict):
        raise TypeError(
            "La configuración de la aeronave debe ser un objeto."
        )

    missing_keys = REQUIRED_CONFIG_KEYS.difference(config)

    if missing_keys:
        raise ValueError(
            "Faltan parámetros obligatorios en la configuración: "
            f"{sorted(missing_keys)}"
        )

    aircraft_id = config["aircraft_id"]

    if not isinstance(aircraft_id, str) or not aircraft_id.strip():
        raise ValueError(
            "El identificador de la aeronave no puede estar vacío."
        )

    origin = validate_airport_code(
        config["origin"],
        "origin",
    )

    validate_route(
        config["route"],
        origin,
    )

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
            "La cantidad mínima de cargas prioritarias "
            "debe ser un número entero."
        )

    if minimum_priority < 0:
        raise ValueError(
            "La cantidad mínima de cargas prioritarias "
            "no puede ser negativa."
        )

    validate_compartments(
        config["compartments"],
        max_weight_kg,
        max_volume_m3,
    )

    validate_incompatible_cargo_pairs(
        config["incompatible_cargo_pairs"]
    )


def validate_route(
    route: Any,
    origin: str,
) -> None:
    if not isinstance(route, list):
        raise TypeError(
            "El parámetro 'route' debe ser una lista."
        )

    if not route:
        raise ValueError(
            "La ruta debe contener al menos una escala o destino."
        )

    sequences: list[int] = []
    airport_codes: list[str] = []

    for position, stop in enumerate(
        route,
        start=1,
    ):
        if not isinstance(stop, dict):
            raise TypeError(
                "Cada escala de la ruta debe estar representada "
                "por un objeto de configuración."
            )

        missing_keys = REQUIRED_ROUTE_STOP_KEYS.difference(stop)

        if missing_keys:
            raise ValueError(
                f"La escala de la posición {position} "
                "no contiene todos los parámetros obligatorios: "
                f"{sorted(missing_keys)}"
            )

        sequence = stop["sequence"]

        if isinstance(sequence, bool) or not isinstance(
            sequence,
            int,
        ):
            raise TypeError(
                f"La secuencia de la escala {position} "
                "debe ser un número entero."
            )

        if sequence <= 0:
            raise ValueError(
                "Las secuencias de la ruta deben ser "
                "mayores que cero."
            )

        airport_code = validate_airport_code(
            stop["airport_code"],
            f"route[{position}].airport_code",
        )

        sequences.append(sequence)
        airport_codes.append(airport_code)

    validate_consecutive_sequence(
        sequences,
        "ruta",
    )

    duplicated_airports = {
        airport_code
        for airport_code in airport_codes
        if airport_codes.count(airport_code) > 1
    }

    if duplicated_airports:
        raise ValueError(
            "Existen aeropuertos duplicados en la ruta: "
            f"{sorted(duplicated_airports)}"
        )

    if origin in airport_codes:
        raise ValueError(
            "El aeropuerto de origen no puede repetirse "
            "dentro de la ruta."
        )


def validate_airport_code(
    value: Any,
    parameter_name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            f"El parámetro '{parameter_name}' "
            "debe ser una cadena de texto."
        )

    normalized_value = value.strip().upper()

    if not AIRPORT_CODE_PATTERN.fullmatch(
        normalized_value
    ):
        raise ValueError(
            f"El parámetro '{parameter_name}' debe contener "
            "un código aeroportuario válido de 3 letras."
        )

    return normalized_value


def validate_compartments(
    compartments: Any,
    aircraft_max_weight_kg: float,
    aircraft_max_volume_m3: float,
) -> None:
    if not isinstance(compartments, list):
        raise TypeError(
            "El parámetro 'compartments' debe ser una lista."
        )

    if not compartments:
        raise ValueError(
            "La aeronave debe contener al menos un compartimiento."
        )

    compartment_ids: list[str] = []
    unloading_orders: list[int] = []

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

        missing_keys = REQUIRED_COMPARTMENT_KEYS.difference(
            compartment
        )

        if missing_keys:
            raise ValueError(
                f"El compartimiento de la posición {position} "
                "no contiene todos los parámetros obligatorios: "
                f"{sorted(missing_keys)}"
            )

        compartment_id = compartment["compartment_id"]

        if (
            not isinstance(compartment_id, str)
            or not compartment_id.strip()
        ):
            raise ValueError(
                "El identificador del compartimiento "
                "no puede estar vacío."
            )

        normalized_id = compartment_id.strip().upper()
        compartment_ids.append(normalized_id)

        description = compartment["description"]

        if (
            not isinstance(description, str)
            or not description.strip()
        ):
            raise ValueError(
                f"El compartimiento '{normalized_id}' "
                "debe incluir una descripción."
            )

        unloading_order = compartment["unloading_order"]

        if isinstance(unloading_order, bool) or not isinstance(
            unloading_order,
            int,
        ):
            raise TypeError(
                f"El parámetro '{normalized_id}.unloading_order' "
                "debe ser un número entero."
            )

        if unloading_order <= 0:
            raise ValueError(
                f"El parámetro '{normalized_id}.unloading_order' "
                "debe ser mayor que cero."
            )

        unloading_orders.append(unloading_order)

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
                f"El parámetro '{normalized_id}.allows_hazardous' "
                "debe ser booleano."
            )

        supports_cold_chain = compartment[
            "supports_cold_chain"
        ]

        if not isinstance(supports_cold_chain, bool):
            raise TypeError(
                f"El parámetro '{normalized_id}."
                "supports_cold_chain' debe ser booleano."
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

    validate_consecutive_sequence(
        unloading_orders,
        "orden de descarga de los compartimientos",
    )

    if hazardous_enabled_compartments == 0:
        raise ValueError(
            "Debe existir al menos un compartimiento autorizado "
            "para mercancías peligrosas."
        )

    if cold_chain_enabled_compartments == 0:
        raise ValueError(
            "Debe existir al menos un compartimiento con soporte "
            "para cadena de frío."
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


def validate_consecutive_sequence(
    values: list[int],
    sequence_name: str,
) -> None:
    duplicated_values = {
        value
        for value in values
        if values.count(value) > 1
    }

    if duplicated_values:
        raise ValueError(
            f"Existen valores duplicados en {sequence_name}: "
            f"{sorted(duplicated_values)}"
        )

    expected_values = list(
        range(1, len(values) + 1)
    )

    if sorted(values) != expected_values:
        raise ValueError(
            f"Los valores de {sequence_name} deben ser "
            "consecutivos y comenzar en 1. "
            f"Esperados: {expected_values}. "
            f"Recibidos: {sorted(values)}."
        )


def validate_incompatible_cargo_pairs(
    incompatible_pairs: Any,
) -> None:
    if not isinstance(incompatible_pairs, list):
        raise TypeError(
            "El parámetro 'incompatible_cargo_pairs' "
            "debe ser una lista."
        )

    normalized_pairs: set[tuple[str, str]] = set()

    for position, pair in enumerate(
        incompatible_pairs,
        start=1,
    ):
        if not isinstance(pair, dict):
            raise TypeError(
                "Cada incompatibilidad debe estar representada "
                "por un objeto de configuración."
            )

        missing_keys = REQUIRED_INCOMPATIBILITY_KEYS.difference(
            pair
        )

        if missing_keys:
            raise ValueError(
                f"La incompatibilidad de la posición {position} "
                "no contiene todos los parámetros obligatorios: "
                f"{sorted(missing_keys)}"
            )

        cargo_id_1 = pair["cargo_id_1"]
        cargo_id_2 = pair["cargo_id_2"]
        reason = pair["reason"]

        if not isinstance(cargo_id_1, str) or not cargo_id_1.strip():
            raise ValueError(
                f"La incompatibilidad de la posición {position} "
                "debe incluir un cargo_id_1 válido."
            )

        if not isinstance(cargo_id_2, str) or not cargo_id_2.strip():
            raise ValueError(
                f"La incompatibilidad de la posición {position} "
                "debe incluir un cargo_id_2 válido."
            )

        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(
                f"La incompatibilidad de la posición {position} "
                "debe incluir una razón."
            )

        normalized_cargo_id_1 = cargo_id_1.strip().upper()
        normalized_cargo_id_2 = cargo_id_2.strip().upper()

        if normalized_cargo_id_1 == normalized_cargo_id_2:
            raise ValueError(
                "Una carga no puede ser incompatible consigo misma: "
                f"{normalized_cargo_id_1}."
            )

        normalized_pair = tuple(
            sorted(
                (
                    normalized_cargo_id_1,
                    normalized_cargo_id_2,
                )
            )
        )

        if normalized_pair in normalized_pairs:
            raise ValueError(
                "Existen pares de cargas incompatibles duplicados: "
                f"{normalized_pair}."
            )

        normalized_pairs.add(normalized_pair)


def validate_positive_number(
    value: Any,
    parameter_name: str,
) -> float:
    if isinstance(value, bool) or not isinstance(
        value,
        int | float,
    ):
        raise TypeError(
            f"El parámetro '{parameter_name}' debe ser numérico."
        )

    numeric_value = float(value)

    if numeric_value <= 0:
        raise ValueError(
            f"El parámetro '{parameter_name}' "
            "debe ser mayor que cero."
        )

    return numeric_value