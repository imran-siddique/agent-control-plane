"""
Agent Control Plane - Main Interface

The main control plane that integrates all components:
- Agent Kernel
- Policy Engine
- Execution Engine
- Audit System
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from agent_kernel import (
    AgentKernel, AgentContext, ExecutionRequest, ExecutionResult,
    ActionType, PermissionLevel, PolicyRule
)
from policy_engine import PolicyEngine, ResourceQuota, RiskPolicy, create_default_policies
from execution_engine import (
    ExecutionEngine, ExecutionContext, SandboxLevel,
    file_read_executor, code_execution_executor, api_call_executor
)


class AgentControlPlane:
    """
    Agent Control Plane - Main interface for governed agent execution
    
    This is the primary interface for applications to interact with
    the control plane. It integrates all governance, safety, and
    execution components.
    """
    
    def __init__(self, enable_default_policies: bool = True):
        self.kernel = AgentKernel()
        self.policy_engine = PolicyEngine()
        self.execution_engine = ExecutionEngine()
        
        # Register default executors
        self._register_default_executors()
        
        # Add default policies if requested
        if enable_default_policies:
            self._add_default_policies()
    
    def create_agent(
        self,
        agent_id: str,
        permissions: Optional[Dict[ActionType, PermissionLevel]] = None,
        quota: Optional[ResourceQuota] = None
    ) -> AgentContext:
        """
        Create a new agent with specified permissions and quotas
        
        Args:
            agent_id: Unique identifier for the agent
            permissions: Dictionary of action types to permission levels
            quota: Resource quota for the agent
            
        Returns:
            AgentContext for the created agent session
        """
        # Create agent session in kernel
        context = self.kernel.create_agent_session(agent_id, permissions)
        
        # Set quota if provided
        if quota:
            self.policy_engine.set_quota(agent_id, quota)
        
        return context
    
    def execute_action(
        self,
        agent_context: AgentContext,
        action_type: ActionType,
        parameters: Dict[str, Any],
        execution_context: Optional[ExecutionContext] = None
    ) -> Dict[str, Any]:
        """
        Execute an action on behalf of an agent
        
        This is the main entry point for agent actions. It goes through
        the complete governance pipeline:
        1. Permission check (Kernel)
        2. Policy validation (Policy Engine)
        3. Risk assessment (Kernel)
        4. Rate limiting (Policy Engine)
        5. Execution (Execution Engine)
        6. Audit logging (Kernel)
        
        Args:
            agent_context: Context for the agent making the request
            action_type: Type of action to execute
            parameters: Parameters for the action
            execution_context: Optional execution context (sandboxing, timeouts, etc.)
            
        Returns:
            Dictionary with execution results and metadata
        """
        # 1. Submit request to kernel for permission check
        request = self.kernel.submit_request(agent_context, action_type, parameters)
        
        if request.status.value == "denied":
            return {
                "success": False,
                "error": "Request denied by kernel",
                "request_id": request.request_id,
                "status": request.status.value
            }
        
        # 2. Validate with policy engine
        is_valid, reason = self.policy_engine.validate_request(request)
        if not is_valid:
            return {
                "success": False,
                "error": f"Policy validation failed: {reason}",
                "request_id": request.request_id,
                "status": "policy_violation"
            }
        
        # 3. Validate risk level
        if not self.policy_engine.validate_risk(request, request.risk_score):
            return {
                "success": False,
                "error": "Request risk level too high",
                "request_id": request.request_id,
                "risk_score": request.risk_score,
                "status": "risk_denied"
            }
        
        # 4. Execute through execution engine
        execution_result = self.execution_engine.execute(request, execution_context)
        
        # 5. Update kernel with execution result
        if execution_result["success"]:
            kernel_result = self.kernel.execute(request)
            return {
                "success": True,
                "result": execution_result["result"],
                "request_id": request.request_id,
                "metrics": execution_result.get("metrics", {}),
                "risk_score": request.risk_score
            }
        else:
            return execution_result
    
    def add_policy_rule(self, rule: PolicyRule):
        """Add a custom policy rule"""
        self.kernel.add_policy_rule(rule)
        self.policy_engine.add_custom_rule(rule)
    
    def set_agent_quota(self, agent_id: str, quota: ResourceQuota):
        """Set resource quota for an agent"""
        self.policy_engine.set_quota(agent_id, quota)
    
    def set_risk_policy(self, policy_id: str, policy: RiskPolicy):
        """Set a risk policy"""
        self.policy_engine.set_risk_policy(policy_id, policy)
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive status for an agent"""
        return {
            "agent_id": agent_id,
            "quota_status": self.policy_engine.get_quota_status(agent_id),
            "active_executions": len([
                ctx for ctx in self.execution_engine.get_active_executions().values()
            ]),
            "execution_history": self.execution_engine.get_execution_history(agent_id, limit=10)
        }
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        return self.kernel.get_audit_log()[-limit:]
    
    def get_execution_history(
        self,
        agent_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get execution history"""
        return self.execution_engine.get_execution_history(agent_id, limit)
    
    def _register_default_executors(self):
        """Register default executors for common action types"""
        self.execution_engine.register_executor(ActionType.FILE_READ, file_read_executor)
        self.execution_engine.register_executor(ActionType.CODE_EXECUTION, code_execution_executor)
        self.execution_engine.register_executor(ActionType.API_CALL, api_call_executor)
    
    def _add_default_policies(self):
        """Add default security policies"""
        for policy in create_default_policies():
            self.add_policy_rule(policy)


# Convenience functions for common operations

def create_read_only_agent(control_plane: AgentControlPlane, agent_id: str) -> AgentContext:
    """Create an agent with read-only permissions"""
    permissions = {
        ActionType.FILE_READ: PermissionLevel.READ_ONLY,
        ActionType.DATABASE_QUERY: PermissionLevel.READ_ONLY,
    }
    
    quota = ResourceQuota(
        agent_id=agent_id,
        max_requests_per_minute=30,
        max_requests_per_hour=500,
        allowed_action_types=[ActionType.FILE_READ, ActionType.DATABASE_QUERY]
    )
    
    return control_plane.create_agent(agent_id, permissions, quota)


def create_standard_agent(control_plane: AgentControlPlane, agent_id: str) -> AgentContext:
    """Create an agent with standard permissions"""
    permissions = {
        ActionType.FILE_READ: PermissionLevel.READ_ONLY,
        ActionType.FILE_WRITE: PermissionLevel.READ_WRITE,
        ActionType.API_CALL: PermissionLevel.READ_WRITE,
        ActionType.DATABASE_QUERY: PermissionLevel.READ_ONLY,
        ActionType.CODE_EXECUTION: PermissionLevel.READ_WRITE,
    }
    
    quota = ResourceQuota(
        agent_id=agent_id,
        max_requests_per_minute=60,
        max_requests_per_hour=1000,
        allowed_action_types=[
            ActionType.FILE_READ,
            ActionType.FILE_WRITE,
            ActionType.API_CALL,
            ActionType.DATABASE_QUERY,
            ActionType.CODE_EXECUTION,
        ]
    )
    
    return control_plane.create_agent(agent_id, permissions, quota)


def create_admin_agent(control_plane: AgentControlPlane, agent_id: str) -> AgentContext:
    """Create an agent with admin permissions"""
    permissions = {
        action_type: PermissionLevel.ADMIN
        for action_type in ActionType
    }
    
    quota = ResourceQuota(
        agent_id=agent_id,
        max_requests_per_minute=120,
        max_requests_per_hour=5000,
        allowed_action_types=list(ActionType)
    )
    
    return control_plane.create_agent(agent_id, permissions, quota)
