import pandas as pd
import pytest

from airline_cargo_optimization.data_validation import (
    validate_business_rules,
    validate_cargo_data,
)


def create_valid_cargo_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "cargo_id": [
                "C001",
                "C002",
                "C003",
                "C004",
            ],
            "description": [
                "Vacunas refrigeradas",
                "Baterías de litio",
                "Equipamiento médico",
                "Documentos urgentes",
            ],
            "weight_kg": [
                300,
                350,
                800,
                100,
            ],
            "volume_m3": [
                1.5,
                1.8,
                4.0,
                0.5,
            ],
            "revenue_usd": [
                7200,
                6500,
                6800,
                1800,
            ],
            "priority": [
                3,
                3,
                2,
                3,
            ],
            "is_hazardous": [
                False,
                True,
                False,
                False,
            ],
            "hazard_class": [
                "",
                "CLASS_9",
                "",
                "",
            ],
            "requires_cold_chain": [
                True,
                False,
                False,
                False,
            ],
        }
    )


def create_valid_aircraft_config() -> dict[str, object]:
    return {
        "aircraft_id": "TEST-001",
        "max_weight_kg": 3000,
        "max_volume_m3": 15.0,
        "minimum_priority_3_items": 1,
        "compartments": [
            {
                "compartment_id": "FORWARD",
                "description": "Compartimiento delantero",
                "max_weight_kg": 1000,
                "max_volume_m3": 5.0,
                "allows_hazardous": False,
                "supports_cold_chain": True,
            },
            {
                "compartment_id": "MAIN",
                "description": "Compartimiento principal",
                "max_weight_kg": 1200,
                "max_volume_m3": 6.0,
                "allows_hazardous": True,
                "supports_cold_chain": False,
            },
            {
                "compartment_id": "AFT",
                "description": "Compartimiento trasero",
                "max_weight_kg": 800,
                "max_volume_m3": 4.0,
                "allows_hazardous": False,
                "supports_cold_chain": False,
            },
        ],
    }


def get_compartments(
    config: dict[str, object],
) -> list[dict[str, object]]:
    compartments = config["compartments"]

    assert isinstance(compartments, list)

    return compartments


def test_validate_cargo_data_accepts_valid_data() -> None:
    validate_cargo_data(create_valid_cargo_data())


def test_validate_cargo_data_rejects_empty_data() -> None:
    cargo_data = pd.DataFrame()

    with pytest.raises(
        ValueError,
        match="no contiene registros",
    ):
        validate_cargo_data(cargo_data)


def test_validate_cargo_data_rejects_missing_columns() -> None:
    cargo_data = create_valid_cargo_data().drop(columns=["requires_cold_chain"])

    with pytest.raises(
        ValueError,
        match="Faltan columnas obligatorias",
    ):
        validate_cargo_data(cargo_data)


def test_validate_cargo_data_rejects_duplicate_ids() -> None:
    cargo_data = create_valid_cargo_data()
    cargo_data.loc[1, "cargo_id"] = "C001"

    with pytest.raises(
        ValueError,
        match="duplicados",
    ):
        validate_cargo_data(cargo_data)


def test_validate_cargo_data_rejects_empty_cargo_id() -> None:
    cargo_data = create_valid_cargo_data()
    cargo_data.loc[0, "cargo_id"] = "   "

    with pytest.raises(
        ValueError,
        match="identificador",
    ):
        validate_cargo_data(cargo_data)


def test_validate_cargo_data_rejects_empty_description() -> None:
    cargo_data = create_valid_cargo_data()
    cargo_data.loc[0, "description"] = "   "

    with pytest.raises(
        ValueError,
        match="descripción",
    ):
        validate_cargo_data(cargo_data)


def test_validate_cargo_data_rejects_negative_weight() -> None:
    cargo_data = create_valid_cargo_data()
    cargo_data.loc[0, "weight_kg"] = -100

    with pytest.raises(
        ValueError,
        match="peso",
    ):
        validate_cargo_data(cargo_data)


def test_validate_cargo_data_rejects_zero_volume() -> None:
    cargo_data = create_valid_cargo_data()
    cargo_data.loc[0, "volume_m3"] = 0

    with pytest.raises(
        ValueError,
        match="volumen",
    ):
        validate_cargo_data(cargo_data)


def test_validate_cargo_data_rejects_negative_revenue() -> None:
    cargo_data = create_valid_cargo_data()
    cargo_data.loc[0, "revenue_usd"] = -1

    with pytest.raises(
        ValueError,
        match="ingreso esperado",
    ):
        validate_cargo_data(cargo_data)


def test_validate_cargo_data_rejects_invalid_priority() -> None:
    cargo_data = create_valid_cargo_data()
    cargo_data.loc[0, "priority"] = 5

    with pytest.raises(
        ValueError,
        match="prioridades",
    ):
        validate_cargo_data(cargo_data)


def test_validate_cargo_data_rejects_non_numeric_weight() -> None:
    cargo_data = create_valid_cargo_data()

    cargo_data["weight_kg"] = [
        "300",
        "350",
        "800",
        "100",
    ]

    with pytest.raises(
        TypeError,
        match="weight_kg",
    ):
        validate_cargo_data(cargo_data)


def test_validate_cargo_data_rejects_non_boolean_hazardous() -> None:
    cargo_data = create_valid_cargo_data()

    cargo_data["is_hazardous"] = [
        "False",
        "True",
        "False",
        "False",
    ]

    with pytest.raises(
        TypeError,
        match="is_hazardous",
    ):
        validate_cargo_data(cargo_data)


def test_validate_cargo_data_rejects_non_boolean_cold_chain() -> None:
    cargo_data = create_valid_cargo_data()

    cargo_data["requires_cold_chain"] = [
        "True",
        "False",
        "False",
        "False",
    ]

    with pytest.raises(
        TypeError,
        match="requires_cold_chain",
    ):
        validate_cargo_data(cargo_data)


def test_validate_cargo_data_rejects_hazardous_without_class() -> None:
    cargo_data = create_valid_cargo_data()
    cargo_data.loc[1, "hazard_class"] = ""

    with pytest.raises(
        ValueError,
        match="deben incluir una clase de riesgo",
    ):
        validate_cargo_data(cargo_data)


def test_validate_cargo_data_rejects_invalid_hazard_class() -> None:
    cargo_data = create_valid_cargo_data()
    cargo_data.loc[1, "hazard_class"] = "CLASS_1"

    with pytest.raises(
        ValueError,
        match="clases de riesgo no permitidas",
    ):
        validate_cargo_data(cargo_data)


def test_validate_cargo_data_rejects_non_hazardous_with_class() -> None:
    cargo_data = create_valid_cargo_data()
    cargo_data.loc[0, "hazard_class"] = "CLASS_3"

    with pytest.raises(
        ValueError,
        match="no deben informar una clase de riesgo",
    ):
        validate_cargo_data(cargo_data)


def test_business_rules_accept_valid_data() -> None:
    validate_business_rules(
        create_valid_cargo_data(),
        create_valid_aircraft_config(),
    )


def test_business_rules_reject_unavailable_priority_items() -> None:
    config = create_valid_aircraft_config()
    config["minimum_priority_3_items"] = 4

    with pytest.raises(
        ValueError,
        match="Requeridas: 4",
    ):
        validate_business_rules(
            create_valid_cargo_data(),
            config,
        )


def test_business_rules_reject_priority_items_by_weight() -> None:
    config = create_valid_aircraft_config()
    config["max_weight_kg"] = 50

    with pytest.raises(
        ValueError,
        match="no caben por peso",
    ):
        validate_business_rules(
            create_valid_cargo_data(),
            config,
        )


def test_business_rules_reject_priority_items_by_volume() -> None:
    config = create_valid_aircraft_config()
    config["max_volume_m3"] = 0.2

    with pytest.raises(
        ValueError,
        match="no caben por volumen",
    ):
        validate_business_rules(
            create_valid_cargo_data(),
            config,
        )


def test_business_rules_accepts_hazardous_with_authorized_compartment() -> None:
    validate_business_rules(
        create_valid_cargo_data(),
        create_valid_aircraft_config(),
    )


def test_business_rules_rejects_hazardous_without_authorized_compartment() -> None:
    config = create_valid_aircraft_config()
    compartments = get_compartments(config)

    for compartment in compartments:
        compartment["allows_hazardous"] = False

    with pytest.raises(
        ValueError,
        match="no posee compartimientos autorizados",
    ):
        validate_business_rules(
            create_valid_cargo_data(),
            config,
        )


def test_business_rules_rejects_hazardous_by_weight_capacity() -> None:
    config = create_valid_aircraft_config()
    compartments = get_compartments(config)

    for compartment in compartments:
        if compartment["allows_hazardous"]:
            compartment["max_weight_kg"] = 100

    with pytest.raises(
        ValueError,
        match="capacidad de peso autorizada",
    ):
        validate_business_rules(
            create_valid_cargo_data(),
            config,
        )


def test_business_rules_rejects_hazardous_by_volume_capacity() -> None:
    config = create_valid_aircraft_config()
    compartments = get_compartments(config)

    for compartment in compartments:
        if compartment["allows_hazardous"]:
            compartment["max_volume_m3"] = 1.0

    with pytest.raises(
        ValueError,
        match="capacidad de volumen autorizada",
    ):
        validate_business_rules(
            create_valid_cargo_data(),
            config,
        )


def test_business_rules_accepts_cold_chain_with_supported_compartment() -> None:
    validate_business_rules(
        create_valid_cargo_data(),
        create_valid_aircraft_config(),
    )


def test_business_rules_rejects_cold_chain_without_supported_compartment() -> None:
    config = create_valid_aircraft_config()
    compartments = get_compartments(config)

    for compartment in compartments:
        compartment["supports_cold_chain"] = False

    with pytest.raises(
        ValueError,
        match="no posee compartimientos refrigerados",
    ):
        validate_business_rules(
            create_valid_cargo_data(),
            config,
        )


def test_business_rules_rejects_cold_chain_by_weight_capacity() -> None:
    config = create_valid_aircraft_config()
    compartments = get_compartments(config)

    for compartment in compartments:
        if compartment["supports_cold_chain"]:
            compartment["max_weight_kg"] = 100

    with pytest.raises(
        ValueError,
        match="capacidad de peso refrigerada",
    ):
        validate_business_rules(
            create_valid_cargo_data(),
            config,
        )


def test_business_rules_rejects_cold_chain_by_volume_capacity() -> None:
    config = create_valid_aircraft_config()
    compartments = get_compartments(config)

    for compartment in compartments:
        if compartment["supports_cold_chain"]:
            compartment["max_volume_m3"] = 1.0

    with pytest.raises(
        ValueError,
        match="capacidad de volumen refrigerada",
    ):
        validate_business_rules(
            create_valid_cargo_data(),
            config,
        )
