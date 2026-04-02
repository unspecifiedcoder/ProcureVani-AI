from apps.agents.nodes.compliance import compliance_node


async def test_compliance_node_returns_guidance_for_passing_case() -> None:
    result = await compliance_node(
        {
            "product_name": "LED Lamps",
            "hs_code": "8539",
            "raw_material_value": 100000.0,
            "foreign_input_value": 15000.0,
        }
    )
    assert result["compliance_result"]["compliant"] is True
    assert result["buyer_class"] == "Class I Local Supplier"
    assert "LED Lamps" in result["compliance_summary"]
    assert "Recommended supporting documents" in result["compliance_guidance"]


async def test_compliance_node_returns_gap_for_failing_case() -> None:
    result = await compliance_node(
        {
            "product_name": "Motor Vehicle Parts",
            "hs_code": "8704",
            "local_content_pct": 45.0,
        }
    )
    assert result["compliance_result"]["compliant"] is False
    assert result["compliance_gap"] == 5.0
    assert "Reduce imported input value" in result["compliance_guidance"]
