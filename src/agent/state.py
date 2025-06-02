from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

class AgentType(Enum):
    """Types of agents in the system"""
    ORCHESTRATOR = "orchestrator"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    CODE = "code"
    REVIEW = "review"

class WorkflowStatus(Enum):
    """Status of the workflow"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class WorkflowStep:
    """Represents a step in the workflow"""
    agent_type: AgentType
    status: WorkflowStatus = WorkflowStatus.PENDING
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

class AgentState:
    """
    State management for multi-agent system
    """
    def __init__(self, initial_data: Optional[Dict[str, Any]] = None):
        self.data: Dict[str, Any] = initial_data or {}
        self.workflow: List[WorkflowStep] = []
        self.current_agent: Optional[AgentType] = None
        self.errors: List[str] = []
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from state"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set value in state"""
        self.data[key] = value
    
    def add_workflow_step(self, agent_type: AgentType) -> None:
        """Add a new step to workflow"""
        step = WorkflowStep(agent_type=agent_type)
        self.workflow.append(step)
    
    def update_current_step(self, 
                          status: WorkflowStatus,
                          output: Optional[Dict[str, Any]] = None,
                          error: Optional[str] = None) -> None:
        """Update status of current workflow step"""
        if not self.workflow:
            return
        
        current_step = self.workflow[-1]
        current_step.status = status
        
        if output:
            current_step.output_data.update(output)
        
        if error:
            current_step.errors.append(error)
            self.errors.append(error)
    
    def get_workflow_history(self) -> List[Dict[str, Any]]:
        """Get history of workflow execution"""
        history = []
        for step in self.workflow:
            history.append({
                "agent": step.agent_type.value,
                "status": step.status.value,
                "input": step.input_data,
                "output": step.output_data,
                "errors": step.errors
            })
        return history
    
    def get_last_output(self) -> Optional[Dict[str, Any]]:
        """Get output from last completed step"""
        for step in reversed(self.workflow):
            if step.status == WorkflowStatus.COMPLETED:
                return step.output_data
        return None
    
    def is_workflow_complete(self) -> bool:
        """Check if workflow is complete"""
        return (len(self.workflow) > 0 and 
                all(step.status == WorkflowStatus.COMPLETED 
                    for step in self.workflow))
    
    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.errors) > 0
    
    def clear_workflow(self) -> None:
        """Clear workflow history"""
        self.workflow.clear()
        self.errors.clear()
        self.current_agent = None
    
    def set_current_agent(self, agent_type: AgentType) -> None:
        """Set current active agent"""
        self.current_agent = agent_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        return {
            "data": self.data,
            "workflow": self.get_workflow_history(),
            "current_agent": self.current_agent.value if self.current_agent else None,
            "errors": self.errors
        }
