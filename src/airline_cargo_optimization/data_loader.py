from pathlib import Path

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
    "requires_cold_chain",
    "destination",
}

BOOLEAN_COLUMNS = {
    "is_hazardous",
    "requires_cold_chain",
}


def load_cargo_data(
    file_path: str | Path,
) -> pd.DataFrame:
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"No existe el archivo de cargas: {path}"
        )

    cargo_data = pd.read_csv(
        path,
        keep_default_na=False,
    )

    missing_columns = REQUIRED_COLUMNS.difference(
        cargo_data.columns
    )

    if missing_columns:
        raise ValueError(
            "Faltan columnas obligatorias: "
            f"{sorted(missing_columns)}"
        )

    for column in BOOLEAN_COLUMNS:
        cargo_data[column] = normalize_boolean_column(
            cargo_data[column],
            column,
        )

    cargo_data["cargo_id"] = (
        cargo_data["cargo_id"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    cargo_data["destination"] = (
        cargo_data["destination"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    invalid_destinations = cargo_data[
        ~cargo_data["destination"].str.fullmatch(
            r"[A-Z]{3}"
        )
    ]

    if not invalid_destinations.empty:
        invalid_values = sorted(
            set(
                invalid_destinations[
                    "destination"
                ].tolist()
            )
        )

        raise ValueError(
            "La columna 'destination' contiene códigos "
            "aeroportuarios inválidos: "
            f"{invalid_values}"
        )

    return cargo_data


def normalize_boolean_column(
    column_data: pd.Series,
    column_name: str,
) -> pd.Series:
    normalized_values = (
        column_data.astype(str)
        .str.strip()
        .str.lower()
    )

    invalid_values = set(
        normalized_values[
            ~normalized_values.isin(
                {"true", "false"}
            )
        ].tolist()
    )

    if invalid_values:
        raise ValueError(
            f"La columna '{column_name}' contiene valores "
            f"booleanos inválidos: {sorted(invalid_values)}"
        )

    return normalized_values.map(
        {
            "true": True,
            "false": False,
        }
    )