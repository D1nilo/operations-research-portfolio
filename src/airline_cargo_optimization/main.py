from airline_cargo_optimization.config import load_aircraft_config
from airline_cargo_optimization.data_loader import load_cargo_data
from airline_cargo_optimization.data_validation import validate_cargo_data
from airline_cargo_optimization.model import build_cargo_model
from airline_cargo_optimization.results import build_solution_summary
from airline_cargo_optimization.solver import solve_cargo_model


def main() -> None:
    cargo_data = load_cargo_data(
        "data/sample/cargo_items.csv"
    )

    validate_cargo_data(cargo_data)

    aircraft_config = load_aircraft_config(
        "configs/aircraft_config.json"
    )

    model = build_cargo_model(
        cargo_data,
        aircraft_config,
    )

    result = solve_cargo_model(
        model,
        cargo_data,
    )

    summary = build_solution_summary(
        result,
        aircraft_config,
    )

    print("\nEstado de la solución:")
    print(summary.status)

    print("\nCargas seleccionadas:")
    print(result.selected_cargo.to_string(index=False))

    print("\nResumen ejecutivo:")
    print(f"Aeronave: {summary.aircraft_id}")
    print(f"Cargas seleccionadas: {summary.selected_items}")
    print(
        f"Ingreso total: USD "
        f"{summary.total_revenue_usd:,.2f}"
    )
    print(
        f"Peso utilizado: "
        f"{summary.total_weight_kg:,.2f} kg"
    )
    print(
        f"Volumen utilizado: "
        f"{summary.total_volume_m3:,.2f} m³"
    )
    print(
        f"Utilización de peso: "
        f"{summary.weight_utilization_pct:.2f}%"
    )
    print(
        f"Utilización de volumen: "
        f"{summary.volume_utilization_pct:.2f}%"
    )


if __name__ == "__main__":
    main()