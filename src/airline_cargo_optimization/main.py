from airline_cargo_optimization.config import load_aircraft_config
from airline_cargo_optimization.data_loader import load_cargo_data


def main() -> None:
    cargo_data = load_cargo_data("data/sample/cargo_items.csv")
    aircraft_config = load_aircraft_config(
        "configs/aircraft_config.json"
    )

    print("\nCargas disponibles:")
    print(cargo_data.to_string(index=False))

    print("\nConfiguración del avión:")
    print(aircraft_config)


if __name__ == "__main__":
    main()