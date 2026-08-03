import json
from pathlib import Path
from typing import Any


def load_aircraft_config(file_path: str | Path) -> dict[str, Any]:
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"No existe el archivo de configuración: {path}"
        )

    with path.open(encoding="utf-8") as file:
        return json.load(file)