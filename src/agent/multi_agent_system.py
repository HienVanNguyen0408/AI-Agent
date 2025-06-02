from agent import (
    AgentState,
    OrchestratorAgent,
    ResearchAgent,
    AnalysisAgent,
    CodeAgent,
    ReviewAgent,
)
from typing import Dict, Any


class MultiAgentSystem:
    """
    Hệ thống Multi Agent điều phối các agent con để xử lý yêu cầu
    """

    def __init__(self):
        # Khởi tạo các agent
        self.orchestrator = OrchestratorAgent()
        self.research = ResearchAgent()
        self.analysis = AnalysisAgent()
        self.code = CodeAgent()
        self.review = ReviewAgent()

        # Map agent type -> instance
        self.agents = {
            "orchestrator": self.orchestrator,
            "research": self.research,
            "analysis": self.analysis,
            "code": self.code,
            "review": self.review,
        }

    async def process_request(self, request: str) -> Dict[str, Any]:
        """
        Xử lý một yêu cầu từ người dùng

        Args:
            request (str): Yêu cầu từ người dùng

        Returns:
            Dict[str, Any]: Kết quả xử lý
        """
        try:
            # 1. Khởi tạo state
            state = AgentState({"request": request})

            # 2. Orchestrator phân tích và tạo workflow
            state = await self.orchestrator.process(state)

            # 3. Thực thi workflow
            while True:
                # Lấy agent tiếp theo cần chạy
                next_agent_type = self.orchestrator.get_next_agent(state)
                if not next_agent_type:
                    break

                # Lấy instance của agent
                agent = self.agents[next_agent_type.value]

                # Validate state trước khi chạy
                if not await agent.validate_state(state):
                    raise ValueError(f"Invalid state for agent {next_agent_type.value}")

                # Chạy agent
                state = await agent.process(state)

                # Cập nhật workflow
                await self.orchestrator.handle_agent_result(
                    next_agent_type, state.get_last_output(), state
                )

            # 4. Trả về kết quả cuối cùng
            if not state.is_workflow_complete():
                raise ValueError("Workflow did not complete successfully")

            return {
                "workflow_history": state.get_workflow_history(),
                "final_result": state.get_last_output(),
            }

        except Exception as e:
            print(f"Error processing request: {str(e)}")
            raise


async def process_user_input(user_input: str) -> Dict[str, Any]:
    """
    Hàm helper để xử lý input từ người dùng
    """
    system = MultiAgentSystem()
    return await system.process_request(user_input)
