from langgraph.graph import StateGraph, END
from agent.state import AgentState
from llm.google_llm import get_llm


def start_node(state: AgentState) -> AgentState:
    if not state.get("question"):
        raise ValueError("The 'question' key is missing or empty in the initial state.")
    return state


def llm_node(state: AgentState) -> AgentState:
    llm = get_llm()
    messages = [
        {"role": "system", "content": llm["system_prompt"]},
        {"role": "user", "content": state["question"]},
    ]
    result = llm["llm"].invoke(messages)
    new_state = AgentState({"question": state["question"], "answer": result.content})
    return new_state


def end_node(state: AgentState):
    if not state.get("answer"):
        raise ValueError("The 'answer' key is missing in the final state.")
    return state


def get_ai_answer(prompt: str) -> str:
    """
    Hàm này xử lý câu hỏi và trả về câu trả lời từ AI Agent.
    """
    # Tạo AI Agent
    agent = create_agent()
    # Khởi tạo trạng thái với câu hỏi
    initial_state = AgentState({"question": prompt})
    result = agent.invoke(initial_state)
    return result["answer"]


# Tạo graph: START → LLM → END
def create_agent():
    builder = StateGraph(AgentState)

    builder.add_node("START", start_node)
    builder.add_node("LLM", llm_node)
    builder.add_node("END", end_node)

    builder.set_entry_point("START")
    builder.add_edge("START", "LLM")
    builder.add_edge("LLM", "END")
    builder.set_finish_point("END")

    graph = builder.compile()
    return graph
