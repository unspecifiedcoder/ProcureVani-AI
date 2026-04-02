from apps.agents.tools.ppp_mii import calculate_lcv, check_compliance


def test_calculate_lcv() -> None:
    assert calculate_lcv(100000, 25000) == 75.0
    assert calculate_lcv(100000, 0) == 100.0
    assert calculate_lcv(100000, 100000) == 0.0
    assert calculate_lcv(0, 50000) == 0.0


def test_check_compliance_pass() -> None:
    result = check_compliance("8539", 60.0)
    assert result["compliant"] is True
    assert result["rating"] == "GREEN"
    assert result["buyer_class"] == "Class I Local Supplier"
    assert "BOM statement" in result["min_documents"]


def test_check_compliance_fail() -> None:
    result = check_compliance("8539", 40.0)
    assert result["compliant"] is False
    assert result["rating"] == "RED"


def test_check_compliance_amber() -> None:
    result = check_compliance("5208", 75.0)
    assert result["compliant"] is True
    assert result["rating"] == "AMBER"
    assert result["policy_reference"] == "Textiles local sourcing guideline"


def test_check_compliance_returns_gap_when_below_threshold() -> None:
    result = check_compliance("8704", 45.0)
    assert result["gap"] == 5.0
