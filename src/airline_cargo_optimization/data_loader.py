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

    cargo_data["is_hazardous"] = (
        cargo_data["is_hazardous"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(
            {
                "true": True,
                "false": False,
            }
        )
    )

    return cargo_data
