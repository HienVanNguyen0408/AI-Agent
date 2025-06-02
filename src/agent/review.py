from typing import Dict, Any, List
from agent.base import BaseAgent, Tool 
from agent.state import AgentState, AgentType, WorkflowStatus
from llm.google_llm import get_llm

class QualityCheckTool(Tool):
    """Tool kiểm tra chất lượng"""
    def __init__(self):
        super().__init__(
            name="quality_check",
            description="Kiểm tra chất lượng kết quả"
        )
    
    async def execute(self, results: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Implement actual quality check
        return {
            "quality_score": 9.0,
            "issues": [],
            "recommendations": []
        }

class ConsistencyCheckTool(Tool):
    """Tool kiểm tra tính nhất quán"""
    def __init__(self):
        super().__init__(
            name="consistency_check",
            description="Kiểm tra tính nhất quán giữa các kết quả"
        )
    
    async def execute(self, results: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Implement actual consistency check
        return {
            "is_consistent": True,
            "inconsistencies": [],
            "suggestions": []
        }

class ReviewAgent(BaseAgent):
    """
    Review Agent - Tổng hợp và kiểm tra chất lượng
    - Kiểm tra chất lượng kết quả từ các agent khác
    - Đảm bảo tính nhất quán
    - Tạo báo cáo tổng hợp
    """
    
    def __init__(self):
        super().__init__("review")
        self.llm = get_llm()
        
        # Khởi tạo tools
        self.add_tool(QualityCheckTool())
        self.add_tool(ConsistencyCheckTool())
    
    async def check_quality(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kiểm tra chất lượng của kết quả
        """
        quality_tool = self.get_tool("quality_check")
        consistency_tool = self.get_tool("consistency_check")
        
        # Kiểm tra chất lượng
        quality_results = await quality_tool.execute(results)
        
        # Kiểm tra tính nhất quán
        consistency_results = await consistency_tool.execute(results)
        
        return {
            "quality": quality_results,
            "consistency": consistency_results
        }
    
    async def generate_summary(self, 
                             results: Dict[str, Any], 
                             review_results: Dict[str, Any]) -> str:
        """
        Tạo bản tóm tắt tổng hợp
        """
        prompt = f"""
        Tạo báo cáo tổng hợp dựa trên:
        
        Kết quả chi tiết: {results}
        Kết quả review: {review_results}
        
        Bao gồm:
        1. Tóm tắt chính
        2. Các điểm quan trọng
        3. Các vấn đề cần lưu ý
        4. Khuyến nghị (nếu có)
        
        Định dạng markdown.
        """
        
        return await self.llm.agenerate(prompt)
    
    async def create_improvement_plan(self, 
                                   review_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Tạo kế hoạch cải thiện nếu có vấn đề
        """
        if (not review_results["quality"]["issues"] and 
            not review_results["consistency"]["inconsistencies"]):
            return []
            
        prompt = f"""
        Tạo kế hoạch cải thiện dựa trên các vấn đề sau:
        
        Vấn đề chất lượng: {review_results["quality"]["issues"]}
        Vấn đề nhất quán: {review_results["consistency"]["inconsistencies"]}
        
        Trả về danh sách JSON với cấu trúc:
        [
            {{
                "issue": "Mô tả vấn đề",
                "solution": "Giải pháp đề xuất",
                "priority": "high/medium/low"
            }}
        ]
        """
        
        result = await self.llm.agenerate(prompt)
        return eval(result)  # Convert string to list
    
    async def process(self, state: AgentState) -> AgentState:
        """
        Review kết quả từ các agent khác
        """
        try:
            # 1. Thu thập kết quả từ các agent trước
            workflow_results = {}
            for step in state.workflow:
                if step.status == WorkflowStatus.COMPLETED:
                    workflow_results[step.agent_type.value] = step.output_data
            
            # 2. Kiểm tra chất lượng
            review_results = await self.check_quality(workflow_results)
            
            # 3. Tạo kế hoạch cải thiện nếu cần
            improvement_plan = []
            if (review_results["quality"]["issues"] or 
                not review_results["consistency"]["is_consistent"]):
                improvement_plan = await self.create_improvement_plan(review_results)
            
            # 4. Tạo báo cáo tổng hợp
            summary = await self.generate_summary(workflow_results, review_results)
            
            # 5. Cập nhật state
            state.set_current_agent(AgentType.REVIEW)
            state.update_current_step(
                WorkflowStatus.COMPLETED,
                output={
                    "review_results": review_results,
                    "improvement_plan": improvement_plan,
                    "summary": summary
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
    
    async def validate_state(self, state: AgentState) -> bool:
        """
        Kiểm tra state có đủ thông tin cần thiết không
        """
        # Cần ít nhất một kết quả từ agent khác
        return len([
            step for step in state.workflow
            if step.status == WorkflowStatus.COMPLETED
        ]) > 0
