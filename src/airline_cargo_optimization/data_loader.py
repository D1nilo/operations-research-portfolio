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
        raise FileNotFoundError(f"No existe el archivo de cargas: {path}")

    cargo_data = pd.read_csv(
        path,
        keep_default_na=False,
    )

    missing_columns = REQUIRED_COLUMNS.difference(cargo_data.columns)

    if missing_columns:
        raise ValueError(f"Faltan columnas obligatorias: {sorted(missing_columns)}")

    for column in BOOLEAN_COLUMNS:
        normalized_values = cargo_data[column].astype(str).str.strip().str.lower()

        invalid_values = set(
            normalized_values[~normalized_values.isin({"true", "false"})].tolist()
        )

        if invalid_values:
            raise ValueError(
                f"La columna '{column}' contiene valores "
                f"booleanos inválidos: {sorted(invalid_values)}"
            )

        cargo_data[column] = normalized_values.map(
            {
                "true": True,
                "false": False,
            }
        )

    return cargo_data
