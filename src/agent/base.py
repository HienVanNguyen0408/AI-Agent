from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
from agent.state import AgentState

class Tool:
    """Base class for tools that agents can use"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    async def execute(self, **kwargs) -> Any:
        raise NotImplementedError()

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str, tools: Optional[List[Tool]] = None):
        """
        Initialize a base agent
        
        Args:
            name (str): Agent's name/identifier
            tools (List[Tool], optional): List of tools this agent can use
        """
        self.name = name
        self.tools = tools or []
        self.state: Dict[str, Any] = {}
    
    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        """
        Process the current state and return updated state
        
        Args:
            state (AgentState): Current state
            
        Returns:
            AgentState: Updated state after processing
        """
        pass
    
    async def handle_error(self, error: Exception) -> None:
        """
        Handle any errors that occur during processing
        
        Args:
            error (Exception): The error that occurred
        """
        print(f"Error in {self.name}: {str(error)}")
    
    def add_tool(self, tool: Tool) -> None:
        """
        Add a new tool to agent's toolset
        
        Args:
            tool (Tool): Tool to add
        """
        self.tools.append(tool)
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """
        Get a tool by name
        
        Args:
            tool_name (str): Name of tool to get
            
        Returns:
            Optional[Tool]: The tool if found, None otherwise
        """
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None
    
    def _update_state(self, key: str, value: Any) -> None:
        """
        Update agent's internal state
        
        Args:
            key (str): State key to update
            value (Any): New value
        """
        self.state[key] = value
    
    def _get_state(self, key: str) -> Optional[Any]:
        """
        Get value from agent's internal state
        
        Args:
            key (str): State key to get
            
        Returns:
            Optional[Any]: Value if found, None otherwise
        """
        return self.state.get(key)
    
    async def validate_state(self, state: AgentState) -> bool:
        """
        Validate if current state has all required data
        
        Args:
            state (AgentState): State to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return True
