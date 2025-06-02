from langgraph.graph import StateGraph, END
from agent.state import AgentState
from llm.google_llm import get_llm
from agent.utils import (
    detect_intent,
    handle_investment,
    handle_gold,
    handle_risk,
    handle_concept,
)


# 1. Khởi động - kiểm tra câu hỏi có tồn tại
def start_node(state: AgentState) -> AgentState:
    if not state.get("question"):
        raise ValueError("Missing 'question' in state.")
    return state


# 2. Xác định ý định câu hỏi
def intent_detection_node(state: AgentState) -> AgentState:
    intent, entities = detect_intent(state["question"])
    state["intent"] = intent
    state["entities"] = entities
    return state


# 3. Router - chuyển hướng tới node xử lý tương ứng
def route_node(state: AgentState) -> str:
    intent = state.get("intent")
    return route_intent(intent)


# 4. Node xử lý từng loại intent
def investment_node(state: AgentState) -> AgentState:
    state["answer"] = handle_investment(state)
    return state


def gold_node(state: AgentState) -> AgentState:
    state["answer"] = handle_gold(state)
    return state


def risk_node(state: AgentState) -> AgentState:
    state["answer"] = handle_risk(state)
    return state


def concept_node(state: AgentState) -> AgentState:
    state["answer"] = handle_concept(state)
    return state


# 5. Kết thúc
def end_node(state: AgentState) -> AgentState:
    if not state.get("answer"):
        raise ValueError("Missing 'answer' in final state.")
    return state


# Hàm trả lời
def get_ai_answer(prompt: str) -> str:
    agent = create_agent()
    initial_state = AgentState({"question": prompt})
    result = agent.invoke(initial_state)
    return result["answer"]


# Tạo graph đa node
def create_agent():
    builder = StateGraph(AgentState)

    # Thêm các node
    builder.add_node("START", start_node)
    builder.add_node("INTENT", intent_detection_node)
    builder.add_node("ROUTER", route_node)
    builder.add_node("INVESTMENT", investment_node)
    builder.add_node("GOLD", gold_node)
    builder.add_node("RISK", risk_node)
    builder.add_node("CONCEPT", concept_node)
    builder.add_node("END", end_node)

    # Kết nối các node
    builder.set_entry_point("START")
    builder.add_edge("START", "INTENT")
    builder.add_edge("INTENT", "ROUTER")

    # Router → node chuyên trách
    builder.add_conditional_edges(
        "ROUTER",
        {
            "investment": "INVESTMENT",
            "gold": "GOLD",
            "risk": "RISK",
            "concept": "CONCEPT",
        },
    )

    # Mỗi node chuyên trách → END
    for node in ["INVESTMENT", "GOLD", "RISK", "CONCEPT"]:
        builder.add_edge(node, "END")

    builder.set_finish_point("END")

    return builder.compile()


from agent.agent import investment_node, gold_node, risk_node, concept_node

def route_intent(intent: str):
    intent_map = {
        "investment": investment_node,
        "gold": gold_node,
        "risk": risk_node,
        "concept": concept_node,
        "other": concept_node,  # mặc định fallback giải thích khái niệm
    }
    return intent_map.get(intent, concept_node)
