from apps.agents.tools.ppp_mii import calculate_lcv, check_compliance


def test_calculate_lcv_uses_foreign_inputs() -> None:
    assert calculate_lcv(100000, 20000) == 80.0


def test_check_compliance_returns_green_when_above_threshold() -> None:
    result = check_compliance("8539", 84.2)
    assert result["compliant"] is True
    assert result["threshold"] == 50
    assert result["rating"] == "GREEN"


def test_check_compliance_returns_gap_when_below_threshold() -> None:
    result = check_compliance("8704", 45.0)
    assert result["compliant"] is False
    assert result["gap"] == 5.0
    assert result["rating"] == "RED"
