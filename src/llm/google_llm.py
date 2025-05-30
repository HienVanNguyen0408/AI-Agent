from langchain_google_genai import ChatGoogleGenerativeAI
from config.config import load_config


class LLM:
    llm = None


def get_google_llm(llm_config):
    # Khởi tạo LLM
    return ChatGoogleGenerativeAI(
        model=llm_config.get("model", "gemini-2.0-flash"),  # Model ngôn ngữ lớn"
        temperature=llm_config.get(
            "temperature", 0.7
        ),  # Mức độ sáng tạo của model, từ 0 tới 1.
        max_tokens=None,  # Giới hạn token của Input, Output. Thường nên để tối đa 32K.
        timeout=None,
        max_retries=llm_config.get("max_retries", 2),
        google_api_key=llm_config.get("api_key"),  # API key đã lấy ở trên
    )


def get_llm():
    # Load config
    config = load_config()
    # Lấy thông tin từ config
    llm_config = config.get("llm_google", {})
    """
    Hàm này trả về LLM đã được cấu hình.
    """
    # Define system_prompt
    system_prompt = config.get("system_prompt", "")
    return {
        "llm": get_google_llm(llm_config),
        "system_prompt": system_prompt,
    }
