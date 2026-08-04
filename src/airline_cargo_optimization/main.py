from airline_cargo_optimization.config import load_aircraft_config
from airline_cargo_optimization.data_loader import load_cargo_data
from airline_cargo_optimization.data_validation import (
    validate_business_rules,
    validate_cargo_data,
)
from airline_cargo_optimization.exporter import (
    export_selected_cargo_csv,
    export_solution_summary_json,
)
from airline_cargo_optimization.model import build_cargo_model
from airline_cargo_optimization.results import build_solution_summary
from airline_cargo_optimization.solver import solve_cargo_model
from airline_cargo_optimization.visualization import (
    create_capacity_utilization_chart,
    create_selected_cargo_revenue_chart,
)


def main() -> None:
    cargo_data = load_cargo_data("data/sample/cargo_items.csv")

    validate_cargo_data(cargo_data)

    aircraft_config = load_aircraft_config("configs/aircraft_config.json")

    validate_business_rules(
        cargo_data,
        aircraft_config,
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

    capacity_chart = create_capacity_utilization_chart(
        summary,
        "reports/figures/capacity_utilization.png",
    )

    revenue_chart = create_selected_cargo_revenue_chart(
        result,
        "reports/figures/selected_cargo_revenue.png",
    )

    selected_cargo_file = export_selected_cargo_csv(
        result,
        "reports/results/selected_cargo.csv",
    )

    summary_file = export_solution_summary_json(
        summary,
        result,
        "reports/results/solution_summary.json",
    )

    print("\n" + "=" * 70)
    print("RESULTADO DE LA OPTIMIZACIÓN")
    print("=" * 70)

    print(f"Estado                 : {summary.status}")
    print(f"Aeronave               : {summary.aircraft_id}")
    print(f"Cargas seleccionadas   : {summary.selected_items}")
    print(f"Ingreso total          : USD {summary.total_revenue_usd:,.2f}")
    print(f"Peso utilizado         : {summary.total_weight_kg:.2f} kg")
    print(f"Volumen utilizado      : {summary.total_volume_m3:.2f} m³")
    print(f"Uso de peso            : {summary.weight_utilization_pct:.2f}%")
    print(f"Uso de volumen         : {summary.volume_utilization_pct:.2f}%")

    print("\n" + "=" * 70)
    print("MÉTRICAS DEL SOLVER")
    print("=" * 70)

    print(f"Valor objetivo         : {result.objective_value:,.2f}")
    print(f"Tiempo de resolución   : {result.wall_time_ms} ms")
    print(f"Iteraciones            : {result.iterations}")
    print(f"Nodos explorados       : {result.nodes}")
    print(f"Variables              : {result.variable_count}")
    print(f"Restricciones          : {result.constraint_count}")

    print("\n" + "=" * 70)
    print("CARGAS SELECCIONADAS")
    print("=" * 70)

    print(result.selected_cargo.to_string(index=False))

    print("\n" + "=" * 70)
    print("ARCHIVOS GENERADOS")
    print("=" * 70)

    print(capacity_chart)
    print(revenue_chart)
    print(selected_cargo_file)
    print(summary_file)


if __name__ == "__main__":
    main()
