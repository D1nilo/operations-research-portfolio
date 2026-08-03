from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from airline_cargo_optimization.results import CargoSolutionSummary
from airline_cargo_optimization.solver import CargoOptimizationResult


def create_capacity_utilization_chart(
    summary: CargoSolutionSummary,
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    categories = ["Peso", "Volumen"]
    utilization = [
        summary.weight_utilization_pct,
        summary.volume_utilization_pct,
    ]

    figure, axis = plt.subplots(figsize=(8, 5))
    bars = axis.bar(categories, utilization)

    axis.set_title("Utilización de capacidad de la aeronave")
    axis.set_ylabel("Utilización (%)")
    axis.set_ylim(0, 110)

    for bar, value in zip(bars, utilization, strict=True):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 2,
            f"{value:.1f}%",
            ha="center",
        )

    figure.tight_layout()
    figure.savefig(path, dpi=150)
    plt.close(figure)

    return path


def create_selected_cargo_revenue_chart(
    result: CargoOptimizationResult,
    output_path: str | Path,
) -> Path:
    if result.selected_cargo.empty:
        raise ValueError("No existen cargas seleccionadas para generar el gráfico.")

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    cargo_ids = result.selected_cargo["cargo_id"]
    revenues = result.selected_cargo["revenue_usd"]

    figure, axis = plt.subplots(figsize=(10, 6))
    bars = axis.bar(cargo_ids, revenues)

    axis.set_title("Ingresos de las cargas seleccionadas")
    axis.set_xlabel("Identificador de carga")
    axis.set_ylabel("Ingreso esperado (USD)")

    for bar, value in zip(bars, revenues, strict=True):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"USD {value:,.0f}",
            ha="center",
            va="bottom",
        )

    figure.tight_layout()
    figure.savefig(path, dpi=150)
    plt.close(figure)

    return path
