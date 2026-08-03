import pandas as pd


REQUIRED_COLUMNS = {
    "cargo_id",
    "description",
    "weight_kg",
    "volume_m3",
    "revenue_usd",
    "priority",
}

NUMERIC_COLUMNS = {
    "weight_kg",
    "volume_m3",
    "revenue_usd",
    "priority",
}

ALLOWED_PRIORITIES = {1, 2, 3}


def validate_cargo_data(cargo_data: pd.DataFrame) -> None:
    if cargo_data.empty:
        raise ValueError("El archivo de cargas no contiene registros.")

    missing_columns = REQUIRED_COLUMNS.difference(cargo_data.columns)

    if missing_columns:
        raise ValueError(f"Faltan columnas obligatorias: {sorted(missing_columns)}")

    if cargo_data[list(REQUIRED_COLUMNS)].isnull().any().any():
        null_columns = cargo_data.columns[cargo_data.isnull().any()].tolist()

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
