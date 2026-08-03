from airline_cargo_optimization.config import load_aircraft_config
from airline_cargo_optimization.data_loader import load_cargo_data
from airline_cargo_optimization.data_validation import validate_cargo_data
from airline_cargo_optimization.model import build_cargo_model
from airline_cargo_optimization.solver import solve_cargo_model


def main() -> None:
    cargo_data = load_cargo_data("data/sample/cargo_items.csv")

    validate_cargo_data(cargo_data)

    aircraft_config = load_aircraft_config("configs/aircraft_config.json")

    model = build_cargo_model(
        cargo_data,
        aircraft_config,
    )

    result = solve_cargo_model(
        model,
        cargo_data,
    )

    print("\nEstado de la solución:")
    print(result.status)

    print("\nCargas seleccionadas:")
    print(
        result.selected_cargo.to_string(
            index=False,
        )
    )

    print("\nResumen de la solución:")
    print(f"Ingreso total: USD {result.total_revenue_usd:,.2f}")
    print(f"Peso utilizado: {result.total_weight_kg:,.2f} kg")
    print(f"Volumen utilizado: {result.total_volume_m3:,.2f} m³")


if __name__ == "__main__":
    main()
