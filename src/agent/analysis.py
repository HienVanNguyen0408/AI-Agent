from typing import Dict, Any, List
from agent.base import BaseAgent, Tool
from agent.state import AgentState, AgentType, WorkflowStatus
from llm.google_llm import get_llm

class DataAnalysisTool(Tool):
    """Tool phân tích dữ liệu"""
    def __init__(self):
        super().__init__(
            name="data_analysis",
            description="Phân tích dữ liệu và tìm patterns"
        )
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Implement actual data analysis
        return {
            "patterns": ["Pattern 1", "Pattern 2"],
            "trends": ["Trend 1", "Trend 2"],
            "correlations": ["Correlation 1", "Correlation 2"]
        }

class InsightGenerationTool(Tool):
    """Tool tạo insights từ dữ liệu"""
    def __init__(self):
        super().__init__(
            name="insight_generation",
            description="Tạo insights và khuyến nghị từ dữ liệu"
        )
    
    async def execute(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Implement actual insight generation
        return {
            "insights": ["Insight 1", "Insight 2"],
            "recommendations": ["Recommendation 1", "Recommendation 2"]
        }

class AnalysisAgent(BaseAgent):
    """
    Analysis Agent - Phân tích dữ liệu và tạo insights
    - Phân tích dữ liệu từ Research Agent
    - Tìm patterns và trends
    - Tạo insights và khuyến nghị
    """
    
    def __init__(self):
        super().__init__("analysis")
        self.llm = get_llm()
        
        # Khởi tạo tools
        self.add_tool(DataAnalysisTool())
        self.add_tool(InsightGenerationTool())
    
    async def analyze_research_data(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phân tích dữ liệu từ Research Agent
        """
        # 1. Extract thông tin từ research data
        analysis = research_data.get("analysis", {})
        results = research_data.get("results", [])
        
        # 2. Phân tích chi tiết
        data_analysis_tool = self.get_tool("data_analysis")
        analysis_results = await data_analysis_tool.execute({
            "summary": analysis.get("summary", ""),
            "results": results
        })
        
        # 3. Tạo insights
        insight_tool = self.get_tool("insight_generation")
        insights = await insight_tool.execute(analysis_results)
        
        return {
            "detailed_analysis": analysis_results,
            "insights": insights
        }
    
    async def generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """
        Tạo khuyến nghị dựa trên kết quả phân tích
        """
        prompt = f"""
        Dựa trên kết quả phân tích sau, đưa ra 3-5 khuyến nghị cụ thể:
        
        Phân tích: {analysis_results}
        
        Trả về danh sách các khuyến nghị, mỗi khuyến nghị một dòng.
        """
        
        result = await self.llm.agenerate(prompt)
        return [r.strip() for r in result.split("\n") if r.strip()]
    
    async def process(self, state: AgentState) -> AgentState:
        """
        Xử lý và phân tích dữ liệu
        """
        try:
            # 1. Lấy dữ liệu từ Research Agent
            research_data = state.get_last_output()
            if not research_data or "research_data" not in research_data:
                raise ValueError("Missing research data in state")
            
            # 2. Phân tích dữ liệu
            analysis_results = await self.analyze_research_data(
                research_data["research_data"]
            )
            
            # 3. Tạo khuyến nghị
            recommendations = await self.generate_recommendations(analysis_results)
            
            # 4. Cập nhật state
            state.set_current_agent(AgentType.ANALYSIS)
            state.update_current_step(
                WorkflowStatus.COMPLETED,
                output={
                    "analysis_results": analysis_results,
                    "recommendations": recommendations
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
        last_output = state.get_last_output()
        if not last_output:
            return False
        return "research_data" in last_output
    
    async def summarize_analysis(self, analysis_results: Dict[str, Any]) -> str:
        """
        Tạo bản tóm tắt từ kết quả phân tích
        """
        prompt = f"""
        Tóm tắt ngắn gọn các kết quả phân tích sau:
        
        Kết quả phân tích: {analysis_results}
        
        Trả về bản tóm tắt ngắn gọn 2-3 câu.
        """
        
        return await self.llm.agenerate(prompt)
