from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "cargo_id",
    "description",
    "weight_kg",
    "volume_m3",
    "revenue_usd",
    "priority",
}


def load_cargo_data(file_path: str | Path) -> pd.DataFrame:
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"No existe el archivo de cargas: {path}")

    data = pd.read_csv(path)

    missing_columns = REQUIRED_COLUMNS.difference(data.columns)
    if missing_columns:
        raise ValueError(
            f"Faltan columnas obligatorias: {sorted(missing_columns)}"
        )

    return data