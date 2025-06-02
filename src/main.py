import asyncio
from typing import Dict, Any
from llm.google_llm import get_llm
from agent.multi_agent_system import process_user_input  # Import MultiAgentSystem


def main():
    """
    Entry point của ứng dụng
    """
    while True:
        try:
            # Nhận input từ user
            user_input = input("\nNhập yêu cầu của bạn (hoặc 'quit' để thoát): ")

            if user_input.lower() == "quit":
                break

            # Xử lý yêu cầu
            result = asyncio.run(process_user_input(user_input))

            # In kết quả
            print("\nKết quả:")
            print("--------")
            print(f"Workflow: {result['workflow_history']}")
            print(f"Kết quả cuối cùng: {result['final_result']}")

        except Exception as e:
            print(f"\nLỗi: {str(e)}")
            continue


if __name__ == "__main__":
    main()
