from typing import Dict, Any, List, Optional
from agent.base import BaseAgent, Tool
from agent.state import AgentState, AgentType, WorkflowStatus
from llm.google_llm import get_llm

class CodeGenerationTool(Tool):
    """Tool tạo code"""
    def __init__(self):
        super().__init__(
            name="code_generation",
            description="Tạo code dựa trên yêu cầu"
        )
    
    async def execute(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Implement actual code generation
        return {
            "code": "print('Hello World')",
            "language": "python",
            "files": {
                "main.py": "print('Hello World')"
            }
        }

class CodeReviewTool(Tool):
    """Tool review code"""
    def __init__(self):
        super().__init__(
            name="code_review",
            description="Kiểm tra chất lượng code"
        )
    
    async def execute(self, code: str) -> Dict[str, Any]:
        # TODO: Implement actual code review
        return {
            "issues": [],
            "suggestions": [],
            "quality_score": 9.5
        }

class TestGenerationTool(Tool):
    """Tool tạo test cases"""
    def __init__(self):
        super().__init__(
            name="test_generation",
            description="Tạo test cases cho code"
        )
    
    async def execute(self, code: str) -> Dict[str, Any]:
        # TODO: Implement actual test generation
        return {
            "test_cases": [
                {
                    "name": "test_basic",
                    "code": "def test_basic(): assert True"
                }
            ]
        }

class CodeAgent(BaseAgent):
    """
    Code Agent - Viết và kiểm tra code
    - Tạo code từ yêu cầu và analysis
    - Review và cải thiện code
    - Tạo test cases
    """
    
    def __init__(self):
        super().__init__("code")
        self.llm = get_llm()
        
        # Khởi tạo tools
        self.add_tool(CodeGenerationTool())
        self.add_tool(CodeReviewTool())
        self.add_tool(TestGenerationTool())
    
    async def create_code_spec(self, 
                             analysis_results: Dict[str, Any], 
                             request: str) -> Dict[str, Any]:
        """
        Tạo specification cho code từ kết quả phân tích
        """
        prompt = f"""
        Tạo specification chi tiết cho code dựa trên:
        
        Yêu cầu: {request}
        Kết quả phân tích: {analysis_results}
        
        Trả về JSON với cấu trúc:
        {{
            "description": "Mô tả chi tiết",
            "requirements": ["Yêu cầu 1", "Yêu cầu 2"],
            "architecture": {{
                "components": ["Component 1", "Component 2"],
                "relationships": ["Relationship 1"]
            }},
            "interfaces": ["Interface 1"],
            "data_structures": ["Structure 1"]
        }}
        """
        
        result = await self.llm.agenerate(prompt)
        return eval(result)  # Convert string to dict
    
    async def generate_code(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tạo code dựa trên specification
        """
        code_tool = self.get_tool("code_generation")
        return await code_tool.execute(spec)
    
    async def review_code(self, code: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review code đã tạo
        """
        review_tool = self.get_tool("code_review")
        test_tool = self.get_tool("test_generation")
        
        # Review code
        review_results = await review_tool.execute(
            str(code.get("files", code.get("code", "")))
        )
        
        # Tạo tests
        test_results = await test_tool.execute(
            str(code.get("files", code.get("code", "")))
        )
        
        return {
            "review": review_results,
            "tests": test_results
        }
    
    async def improve_code(self, 
                         code: Dict[str, Any],
                         review_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cải thiện code dựa trên kết quả review
        """
        prompt = f"""
        Cải thiện code dựa trên các issues và suggestions:
        
        Code hiện tại:
        {code}
        
        Review results:
        {review_results}
        
        Trả về code đã được cải thiện.
        """
        
        improved_code = await self.llm.agenerate(prompt)
        return {
            "code": improved_code,
            "original": code,
            "improvements": review_results
        }
    
    async def process(self, state: AgentState) -> AgentState:
        """
        Xử lý yêu cầu code
        """
        try:
            # 1. Lấy kết quả phân tích và yêu cầu
            analysis_data = state.get_last_output()
            request = state.get("request")
            
            if not analysis_data or not request:
                raise ValueError("Missing analysis data or request")
            
            # 2. Tạo specification
            spec = await self.create_code_spec(
                analysis_data.get("analysis_results", {}),
                request
            )
            
            # 3. Tạo code
            code = await self.generate_code(spec)
            
            # 4. Review và test
            review_results = await self.review_code(code)
            
            # 5. Cải thiện code nếu cần
            if review_results["review"]["issues"]:
                code = await self.improve_code(code, review_results)
            
            # 6. Cập nhật state
            state.set_current_agent(AgentType.CODE)
            state.update_current_step(
                WorkflowStatus.COMPLETED,
                output={
                    "specification": spec,
                    "code": code,
                    "review": review_results
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
        if not last_output or not state.get("request"):
            return False
        return "analysis_results" in last_output
