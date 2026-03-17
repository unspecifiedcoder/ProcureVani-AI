import pytest
from apps.agents.tools.ppp_mii import check_compliance, calculate_lcv

def test_calculate_lcv():
    assert calculate_lcv(100000, 25000) == 75.0
    assert calculate_lcv(100000, 0) == 100.0
    assert calculate_lcv(100000, 100000) == 0.0
    assert calculate_lcv(0, 50000) == 0.0

def test_check_compliance_pass():
    result = check_compliance("8539", 60.0)
    assert result["compliant"] == True
    assert result["rating"] == "GREEN"

def test_check_compliance_fail():
    result = check_compliance("8539", 40.0)
    assert result["compliant"] == False
    assert result["rating"] == "RED"

def test_check_compliance_amber():
    result = check_compliance("5208", 75.0)
    assert result["compliant"] == True
    assert result["rating"] == "AMBER"
