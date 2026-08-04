def create_valid_aircraft_config() -> dict[str, object]:
    return {
        "aircraft_id": "TEST-001",
        "max_weight_kg": 3000,
        "max_volume_m3": 15.0,
        "minimum_priority_3_items": 1,
    }


def test_business_rules_accept_feasible_priority_requirement() -> None:
    validate_business_rules(
        create_valid_cargo_data(),
        create_valid_aircraft_config(),
    )


def test_business_rules_reject_unavailable_priority_items() -> None:
    config = create_valid_aircraft_config()
    config["minimum_priority_3_items"] = 3

    with pytest.raises(
        ValueError,
        match="Requeridas: 3",
    ):
        validate_business_rules(
            create_valid_cargo_data(),
            config,
        )


def test_business_rules_reject_priority_items_by_weight() -> None:
    config = create_valid_aircraft_config()
    config["max_weight_kg"] = 300

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
    config["max_volume_m3"] = 1.0

    with pytest.raises(
        ValueError,
        match="no caben por volumen",
    ):
        validate_business_rules(
            create_valid_cargo_data(),
            config,
        )