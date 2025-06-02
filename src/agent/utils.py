from llm.google_llm import get_llm
import json


def detect_intent(question: str):
    """
    Sử dụng LLM phân tích intent trả về JSON gồm:
    {
        "intent": "investment" | "gold" | "risk" | "concept" | "other",
        "entities": {
            "asset_type": "...",
            "investment_horizon": "...",
            "risk_level": "...",
            ...
        }
    }
    """
    llm = get_llm()
    system_prompt = (
        "Bạn là JACK – trợ lý phân tích ý định câu hỏi trong lĩnh vực tài chính. "
        "Phân loại câu hỏi vào một trong các intent: investment, gold, risk, concept, other. "
        "Trích xuất các entities nếu có: asset_type (ví dụ: cổ phiếu, vàng, crypto), investment_horizon (ngắn hạn, dài hạn), risk_level (thấp, trung bình, cao). "
        "Trả về kết quả dưới dạng JSON duy nhất, ví dụ: "
        '{"intent": "investment", "entities": {"asset_type": "cổ phiếu", "investment_horizon": "dài hạn", "risk_level": "cao"}}'
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    response = llm["llm"].invoke(messages).content

    try:
        parsed = json.loads(response)
        intent = parsed.get("intent", "other").lower()
        entities = parsed.get("entities", {})
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        print(f"Response from LLM: {response}")
        # fallback nếu LLM không trả JSON đúng
        intent = "other"
        entities = {}

    return intent, entities


# Dùng chung cho tất cả
def _call_llm_with_prompt(system_prompt: str, user_input: str) -> str:
    llm = get_llm()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]
    result = llm["llm"].invoke(messages)
    return result.content


# 1️⃣ Đầu tư (cổ phiếu, trái phiếu, quỹ, crypto…)
def handle_investment(state):
    question = state["question"]
    system_prompt = (
        "Bạn là JACK – một chuyên gia tư vấn đầu tư tài chính toàn diện. "
        "Hãy phân tích kỹ càng câu hỏi người dùng dưới góc độ tài sản truyền thống (cổ phiếu, trái phiếu, quỹ) "
        "hoặc tài sản số (crypto, DeFi, NFT) tùy theo ngữ cảnh. Trình bày phân tích và khuyến nghị rõ ràng, súc tích, dễ hiểu."
    )
    return _call_llm_with_prompt(system_prompt, question)


# 2️⃣ Vàng (phân tích kỹ thuật + cơ bản + vĩ mô)
def handle_gold(state):
    question = state["question"]
    system_prompt = (
        "Bạn là JACK – chuyên gia phân tích thị trường vàng. "
        "Hãy trả lời câu hỏi của người dùng với kiến thức vĩ mô, phân tích kỹ thuật, phân tích cơ bản về giá vàng (Spot Gold, vàng SJC, v.v.). "
        "Nếu cần, sử dụng các chỉ báo như MA, RSI, Fibonacci hoặc dữ liệu cung-cầu để đưa ra đánh giá xu hướng."
    )
    return _call_llm_with_prompt(system_prompt, question)


# 3️⃣ Rủi ro & tối ưu danh mục
def handle_risk(state):
    question = state["question"]
    system_prompt = (
        "Bạn là JACK – chuyên gia tư vấn quản lý rủi ro và xây dựng danh mục đầu tư. "
        "Hãy giúp người dùng đánh giá rủi ro, khẩu vị đầu tư, phân bổ tài sản và tái cân bằng danh mục nếu cần. "
        "Giải thích các khái niệm như Sharpe Ratio, Alpha, Beta nếu liên quan. Trình bày rõ ràng, dễ hiểu và thực tế."
    )
    return _call_llm_with_prompt(system_prompt, question)


# 4️⃣ Giải thích khái niệm tài chính
def handle_concept(state):
    question = state["question"]
    system_prompt = (
        "Bạn là JACK – chuyên gia giáo dục tài chính. "
        "Hãy giải thích khái niệm tài chính trong câu hỏi của người dùng một cách dễ hiểu, nhưng chính xác về mặt học thuật. "
        "Minh họa bằng ví dụ đơn giản. Giữ phong cách chuyên nghiệp và súc tích."
    )
    return _call_llm_with_prompt(system_prompt, question)
