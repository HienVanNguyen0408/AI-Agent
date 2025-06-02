from typing import Dict, Any, List
from agent.base import BaseAgent, Tool
from agent.state import AgentState, AgentType, WorkflowStatus
from llm.google_llm import get_llm

class WebSearchTool(Tool):
    """Tool thực hiện tìm kiếm web"""
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Tìm kiếm thông tin từ internet"
        )
    
    async def execute(self, query: str) -> List[Dict[str, str]]:
        # TODO: Implement actual web search
        # Mock data for now
        return [
            {
                "title": f"Result for: {query}",
                "snippet": "Sample search result",
                "url": "https://example.com"
            }
        ]

class DocumentAnalysisTool(Tool):
    """Tool phân tích tài liệu"""
    def __init__(self):
        super().__init__(
            name="document_analysis",
            description="Phân tích và trích xuất thông tin từ tài liệu"
        )
    
    async def execute(self, content: str) -> Dict[str, Any]:
        # TODO: Implement actual document analysis
        return {
            "summary": "Sample summary",
            "key_points": ["Point 1", "Point 2"],
            "entities": ["Entity 1", "Entity 2"]
        }

class ResearchAgent(BaseAgent):
    """
    Research Agent - Thu thập và tổ chức thông tin
    - Tìm kiếm thông tin từ nhiều nguồn
    - Phân tích và tổng hợp dữ liệu
    - Chuẩn bị thông tin cho các agent khác
    """
    
    def __init__(self):
        super().__init__("research")
        llm_config = get_llm()
        self.llm = llm_config["llm"]
        
        # Khởi tạo tools
        self.add_tool(WebSearchTool())
        self.add_tool(DocumentAnalysisTool())
    
    async def generate_search_queries(self, request: str) -> List[str]:
        """
        Tạo các câu query tìm kiếm từ yêu cầu
        """
        prompt = f"""
        Từ yêu cầu sau, tạo 3-5 câu query tìm kiếm để thu thập thông tin:
        
        Yêu cầu: {request}
        
        Trả về danh sách các câu query, mỗi câu một dòng.
        """
        
        response = await self.llm.ainvoke(prompt)
        return [q.strip() for q in response.content.split("\n") if q.strip()]
    
    async def analyze_search_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Phân tích kết quả tìm kiếm
        """
        prompt = f"""
        Phân tích các kết quả tìm kiếm sau và tổng hợp thành:
        1. Tóm tắt ngắn gọn
        2. Các điểm chính
        3. Các khái niệm quan trọng
        
        Kết quả tìm kiếm:
        {results}
        """
        
        response = await self.llm.ainvoke(prompt)
        analysis = response.content
        return {
            "summary": analysis,
            "results": results
        }
    
    async def process(self, state: AgentState) -> AgentState:
        """
        Xử lý yêu cầu nghiên cứu
        """
        try:
            # 1. Lấy yêu cầu từ input
            request = state.get("request")
            if not request:
                raise ValueError("Missing research request")
            
            # 2. Tạo các query tìm kiếm
            queries = await self.generate_search_queries(request)
            
            # 3. Thực hiện tìm kiếm
            search_tool = self.get_tool("web_search")
            all_results = []
            
            for query in queries:
                results = await search_tool.execute(query)
                all_results.extend(results)
            
            # 4. Phân tích kết quả
            analysis = await self.analyze_search_results(all_results)
            
            # 5. Cập nhật state
            state.set_current_agent(AgentType.RESEARCH)
            state.update_current_step(
                WorkflowStatus.COMPLETED,
                output={
                    "research_data": {
                        "queries": queries,
                        "results": all_results,
                        "analysis": analysis
                    }
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
        required_keys = ["request"]
        return all(state.get(key) is not None for key in required_keys)
