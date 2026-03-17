# apps/agents/graph.py
# LangGraph compliance pipeline.

from langgraph.graph import StateGraph, END
from apps.agents.state import MSMEState
from apps.agents.nodes.intent import intent_node
from apps.agents.nodes.compliance import compliance_node
from apps.agents.nodes.document import document_node
from apps.agents.nodes.fraud import fraud_node
from apps.agents.nodes.gem import gem_node

def route_by_intent(state: MSMEState) -> str:
    intent = state.get("intent", "other")
    route_map = {"register": "compliance", "check_status": "__end__", "query": "__end__", "help": "__end__", "other": "compliance"}
    return route_map.get(intent, "compliance")

def route_after_compliance(state: MSMEState) -> str:
    if state.get("needs_field"):
        return "__end__"
    compliance = state.get("compliance_result")
    if compliance and compliance.get("compliant"):
        return "document"
    return "__end__"

def route_after_fraud(state: MSMEState) -> str:
    if state.get("fraud_clean", True):
        return "gem_package"
    return "__end__"

def build_compliance_graph():
    graph = StateGraph(MSMEState)
    graph.add_node("intent", intent_node)
    graph.add_node("compliance", compliance_node)
    graph.add_node("document", document_node)
    graph.add_node("fraud_check", fraud_node)
    graph.add_node("gem_package", gem_node)
    
    graph.set_entry_point("intent")
    graph.add_conditional_edges("intent", route_by_intent, {"compliance": "compliance", "__end__": END})
    graph.add_conditional_edges("compliance", route_after_compliance, {"document": "document", "__end__": END})
    graph.add_edge("document", "fraud_check")
    graph.add_conditional_edges("fraud_check", route_after_fraud, {"gem_package": "gem_package", "__end__": END})
    graph.add_edge("gem_package", END)
    
    return graph.compile()

compliance_graph = build_compliance_graph()
