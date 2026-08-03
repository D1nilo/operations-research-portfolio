from airline_cargo_optimization.config import load_aircraft_config
from airline_cargo_optimization.data_loader import load_cargo_data
from airline_cargo_optimization.model import build_cargo_model
from airline_cargo_optimization.solver import solve_cargo_model


def main() -> None:
    cargo_data = load_cargo_data("data/sample/cargo_items.csv")
    aircraft_config = load_aircraft_config(
        "configs/aircraft_config.json"
    )

    solver, selection_variables = build_cargo_model(
        cargo_data,
        aircraft_config,
    )

    results = solve_cargo_model(
        solver,
        selection_variables,
        cargo_data,
    )

    print("\nEstado de la solución:")
    print(results["status"])

    print("\nCargas seleccionadas:")
    print(
        results["selected_cargo"].to_string(
            index=False,
        )
    )

    print("\nResumen:")
    print(
        f"Ingreso total: USD "
        f"{results['total_revenue_usd']:,.2f}"
    )
    print(
        f"Peso utilizado: "
        f"{results['total_weight_kg']:,.2f} kg"
    )
    print(
        f"Volumen utilizado: "
        f"{results['total_volume_m3']:,.2f} m³"
    )


if __name__ == "__main__":
    main()