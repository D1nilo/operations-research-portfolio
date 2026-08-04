from typing import Any

import pandas as pd

REQUIRED_COLUMNS = {
    "cargo_id",
    "description",
    "weight_kg",
    "volume_m3",
    "revenue_usd",
    "priority",
    "is_hazardous",
    "hazard_class",
}

NUMERIC_COLUMNS = {
    "weight_kg",
    "volume_m3",
    "revenue_usd",
    "priority",
}

ALLOWED_PRIORITIES = {1, 2, 3}

ALLOWED_HAZARD_CLASSES = {
    "CLASS_3",
    "CLASS_9",
}


def validate_cargo_data(cargo_data: pd.DataFrame) -> None:
    if cargo_data.empty:
        raise ValueError("El archivo de cargas no contiene registros.")

    missing_columns = REQUIRED_COLUMNS.difference(cargo_data.columns)

    if missing_columns:
        raise ValueError(f"Faltan columnas obligatorias: {sorted(missing_columns)}")

    required_non_nullable_columns = [
        "cargo_id",
        "description",
        "weight_kg",
        "volume_m3",
        "revenue_usd",
        "priority",
        "is_hazardous",
    ]

    if cargo_data[required_non_nullable_columns].isnull().any().any():
        null_columns = (
            cargo_data[required_non_nullable_columns]
            .columns[cargo_data[required_non_nullable_columns].isnull().any()]
            .tolist()
        )

        raise ValueError(f"Existen valores nulos en las columnas: {null_columns}")

    if cargo_data["cargo_id"].duplicated().any():
        duplicated_ids = cargo_data.loc[
            cargo_data["cargo_id"].duplicated(keep=False),
            "cargo_id",
        ].tolist()

        raise ValueError(
            "Existen identificadores de carga duplicados: "
            f"{sorted(set(duplicated_ids))}"
        )

    for column in NUMERIC_COLUMNS:
        if not pd.api.types.is_numeric_dtype(cargo_data[column]):
            raise TypeError(f"La columna '{column}' debe contener valores numéricos.")

    if not pd.api.types.is_bool_dtype(cargo_data["is_hazardous"]):
        raise TypeError("La columna 'is_hazardous' debe contener valores booleanos.")

    if (cargo_data["weight_kg"] <= 0).any():
        raise ValueError("El peso de todas las cargas debe ser mayor que cero.")

    if (cargo_data["volume_m3"] <= 0).any():
        raise ValueError("El volumen de todas las cargas debe ser mayor que cero.")

    if (cargo_data["revenue_usd"] < 0).any():
        raise ValueError("El ingreso esperado no puede contener valores negativos.")

    invalid_priorities = set(
        cargo_data.loc[
            ~cargo_data["priority"].isin(ALLOWED_PRIORITIES),
            "priority",
        ].tolist()
    )

    if invalid_priorities:
        raise ValueError(
            f"Existen prioridades no permitidas: {sorted(invalid_priorities)}"
        )

    empty_descriptions = cargo_data["description"].astype(str).str.strip().eq("")

    if empty_descriptions.any():
        raise ValueError("Todas las cargas deben incluir una descripción.")

    hazardous_cargo = cargo_data[cargo_data["is_hazardous"]]

    hazardous_without_class = (
        hazardous_cargo["hazard_class"].astype(str).str.strip().eq("")
    )

    if hazardous_without_class.any():
        cargo_ids = hazardous_cargo.loc[
            hazardous_without_class,
            "cargo_id",
        ].tolist()

        raise ValueError(
            "Las cargas peligrosas deben incluir "
            "una clase de riesgo. "
            f"Cargas afectadas: {cargo_ids}"
        )

    invalid_hazard_classes = set(
        hazardous_cargo.loc[
            ~hazardous_cargo["hazard_class"].isin(ALLOWED_HAZARD_CLASSES),
            "hazard_class",
        ].tolist()
    )

    if invalid_hazard_classes:
        raise ValueError(
            f"Existen clases de riesgo no permitidas: {sorted(invalid_hazard_classes)}"
        )

    non_hazardous_cargo = cargo_data[~cargo_data["is_hazardous"]]

    non_hazardous_with_class = (
        non_hazardous_cargo["hazard_class"].astype(str).str.strip().ne("")
    )

    if non_hazardous_with_class.any():
        cargo_ids = non_hazardous_cargo.loc[
            non_hazardous_with_class,
            "cargo_id",
        ].tolist()

        raise ValueError(
            "Las cargas no peligrosas no deben "
            "informar una clase de riesgo. "
            f"Cargas afectadas: {cargo_ids}"
        )


def validate_business_rules(
    cargo_data: pd.DataFrame,
    aircraft_config: dict[str, Any],
) -> None:
    minimum_priority_items = int(aircraft_config["minimum_priority_3_items"])

    high_priority_cargo = cargo_data[cargo_data["priority"] == 3]

    available_priority_items = len(high_priority_cargo)

    if minimum_priority_items > available_priority_items:
        raise ValueError(
            "La cantidad mínima de cargas de prioridad 3 "
            "no puede cumplirse. "
            f"Requeridas: {minimum_priority_items}. "
            f"Disponibles: {available_priority_items}."
        )

    if minimum_priority_items > 0:
        lightest_priority_items = high_priority_cargo.nsmallest(
            minimum_priority_items,
            "weight_kg",
        )

        minimum_required_weight = float(lightest_priority_items["weight_kg"].sum())

        if minimum_required_weight > float(aircraft_config["max_weight_kg"]):
            raise ValueError(
                "Las cargas prioritarias mínimas "
                "no caben por peso. "
                "Peso mínimo requerido: "
                f"{minimum_required_weight:.2f} kg. "
                "Capacidad disponible: "
                f"{float(aircraft_config['max_weight_kg']):.2f} kg."
            )

        smallest_priority_items = high_priority_cargo.nsmallest(
            minimum_priority_items,
            "volume_m3",
        )

        minimum_required_volume = float(smallest_priority_items["volume_m3"].sum())

        if minimum_required_volume > float(aircraft_config["max_volume_m3"]):
            raise ValueError(
                "Las cargas prioritarias mínimas "
                "no caben por volumen. "
                "Volumen mínimo requerido: "
                f"{minimum_required_volume:.2f} m³. "
                "Capacidad disponible: "
                f"{float(aircraft_config['max_volume_m3']):.2f} m³."
            )

    hazardous_cargo = cargo_data[cargo_data["is_hazardous"]]

    if hazardous_cargo.empty:
        return

    hazardous_compartments = [
        compartment
        for compartment in aircraft_config["compartments"]
        if compartment["allows_hazardous"]
    ]

    if not hazardous_compartments:
        raise ValueError(
            "Existen cargas peligrosas, pero la aeronave "
            "no posee compartimientos autorizados."
        )

    total_hazardous_weight_capacity = sum(
        float(compartment["max_weight_kg"]) for compartment in hazardous_compartments
    )

    total_hazardous_volume_capacity = sum(
        float(compartment["max_volume_m3"]) for compartment in hazardous_compartments
    )

    lightest_hazardous_weight = float(hazardous_cargo["weight_kg"].min())

    smallest_hazardous_volume = float(hazardous_cargo["volume_m3"].min())

    if lightest_hazardous_weight > total_hazardous_weight_capacity:
        raise ValueError(
            "Ninguna carga peligrosa puede ser transportada "
            "por falta de capacidad de peso autorizada."
        )

    if smallest_hazardous_volume > total_hazardous_volume_capacity:
        raise ValueError(
            "Ninguna carga peligrosa puede ser transportada "
            "por falta de capacidad de volumen autorizada."
        )
