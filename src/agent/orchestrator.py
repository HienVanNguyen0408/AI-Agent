from typing import Dict, List, Any
from abc import ABC
from agent.base import BaseAgent
from agent.state import AgentState, AgentType, WorkflowStatus
from llm.google_llm import get_llm

class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Agent - Điều phối toàn bộ hệ thống multi-agent
    - Phân tích yêu cầu người dùng
    - Tạo và quản lý workflow
    - Điều phối các agent khác
    """
    
    def __init__(self):
        super().__init__("orchestrator")
        llm_config = get_llm()
        self.llm = llm_config["llm"]
        self.workflows: Dict[str, List[AgentType]] = {
            "research": [
                AgentType.RESEARCH,
                AgentType.ANALYSIS,
                AgentType.REVIEW
            ],
            "code": [
                AgentType.RESEARCH,
                AgentType.ANALYSIS, 
                AgentType.CODE,
                AgentType.REVIEW
            ],
            "analysis": [
                AgentType.RESEARCH,
                AgentType.ANALYSIS,
                AgentType.REVIEW
            ]
        }
    
    async def analyze_request(self, request: str) -> str:
        """
        Phân tích yêu cầu người dùng để xác định workflow phù hợp
        """
        prompt = f"""
        Phân tích yêu cầu sau và chọn một trong các workflow:
        - research: Tìm hiểu, nghiên cứu về một chủ đề
        - code: Viết code, implement một tính năng
        - analysis: Phân tích dữ liệu, đưa ra insights

        Yêu cầu: {request}
        
        Trả về một trong các giá trị: research/code/analysis
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content.strip()

    def create_workflow(self, workflow_type: str) -> List[AgentType]:
        """
        Tạo workflow dựa trên loại yêu cầu
        """
        return self.workflows.get(workflow_type, self.workflows["research"])

    async def process(self, state: AgentState) -> AgentState:
        """
        Xử lý yêu cầu và điều phối các agent
        """
        try:
            # 1. Lấy yêu cầu từ user
            request = state.get("request")
            if not request:
                raise ValueError("Missing user request")
                
            # 2. Phân tích yêu cầu
            workflow_type = await self.analyze_request(request)
            
            # 3. Tạo workflow
            workflow = self.create_workflow(workflow_type)
            
            # 4. Set up workflow trong state
            state.clear_workflow()
            for agent_type in workflow:
                state.add_workflow_step(agent_type)
            
            # 5. Khởi tạo workflow với input từ user
            first_step = state.workflow[0]
            first_step.input_data = {
                "request": request,
                "workflow_type": workflow_type
            }
            
            # 6. Cập nhật trạng thái
            state.set_current_agent(AgentType.ORCHESTRATOR)
            state.update_current_step(
                WorkflowStatus.COMPLETED,
                output={
                    "workflow_type": workflow_type,
                    "workflow_steps": [step.agent_type.value for step in state.workflow]
                }
            )
            
            return state
            
        except Exception as e:
            state.update_current_step(
                WorkflowStatus.FAILED,
                error=str(e)
            )
            await self.handle_error(e)
            raise
    
    async def handle_agent_result(self, agent_type: AgentType, result: Dict[str, Any], state: AgentState) -> None:
        """
        Xử lý kết quả từ một agent và cập nhật workflow
        """
        # Tìm step của agent trong workflow
        for step in state.workflow:
            if step.agent_type == agent_type:
                step.status = WorkflowStatus.COMPLETED
                step.output_data = result
                break
                
        # Kiểm tra xem workflow đã hoàn thành chưa
        if state.is_workflow_complete():
            state.set_current_agent(None)
        else:
            # Tìm agent tiếp theo
            current_index = next(
                (i for i, step in enumerate(state.workflow) 
                 if step.agent_type == agent_type), 
                -1
            )
            if current_index < len(state.workflow) - 1:
                next_step = state.workflow[current_index + 1]
                next_step.input_data = result
                state.set_current_agent(next_step.agent_type)
    
    def get_next_agent(self, state: AgentState) -> AgentType:
        """
        Xác định agent tiếp theo cần thực thi
        """
        for step in state.workflow:
            if step.status == WorkflowStatus.PENDING:
                return step.agent_type
        return None
