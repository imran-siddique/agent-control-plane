"""
Agent Control Plane - Main Interface

The main control plane that integrates all components:
- Agent Kernel
- Policy Engine
- Execution Engine
- Audit System
- Shadow Mode (simulation)
- Mute Agent (capability-based)
- Constraint Graphs (multi-dimensional)
- Supervisor Agents (recursive governance)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from .agent_kernel import (
    AgentKernel, AgentContext, ExecutionRequest, ExecutionResult,
    ActionType, PermissionLevel, PolicyRule, ExecutionStatus
)
from .policy_engine import PolicyEngine, ResourceQuota, RiskPolicy, create_default_policies
from .execution_engine import (
    ExecutionEngine, ExecutionContext, SandboxLevel
)
from .example_executors import (
    file_read_executor, code_execution_executor, api_call_executor
)
from .shadow_mode import ShadowModeExecutor, ShadowModeConfig, ReasoningStep
from .mute_agent import MuteAgentValidator, MuteAgentConfig
from .constraint_graphs import (
    DataGraph, PolicyGraph, TemporalGraph, ConstraintGraphValidator
)
from .supervisor_agents import SupervisorAgent, SupervisorNetwork


class AgentControlPlane:
    """
    Agent Control Plane - Main interface for governed agent execution
    
    This is the primary interface for applications to interact with
    the control plane. It integrates all governance, safety, and
    execution components including:
    - Shadow Mode for simulation
    - Mute Agent for capability-based execution
    - Constraint Graphs for multi-dimensional context
    - Supervisor Agents for recursive governance
    """
    
    def __init__(
        self,
        enable_default_policies: bool = True,
        enable_shadow_mode: bool = False,
        enable_constraint_graphs: bool = False
    ):
        self.kernel = AgentKernel()
        self.policy_engine = PolicyEngine()
        self.execution_engine = ExecutionEngine()
        
        # Shadow Mode for simulation
        self.shadow_mode_enabled = enable_shadow_mode
        self.shadow_executor = ShadowModeExecutor(ShadowModeConfig(enabled=enable_shadow_mode))
        
        # Mute Agent validators (per agent)
        self.mute_validators: Dict[str, MuteAgentValidator] = {}
        
        # Constraint Graphs
        self.constraint_graphs_enabled = enable_constraint_graphs
        if enable_constraint_graphs:
            self.data_graph = DataGraph()
            self.policy_graph = PolicyGraph()
            self.temporal_graph = TemporalGraph()
            self.constraint_validator = ConstraintGraphValidator(
                self.data_graph,
                self.policy_graph,
                self.temporal_graph
            )
        else:
            self.data_graph = None
            self.policy_graph = None
            self.temporal_graph = None
            self.constraint_validator = None
        
        # Supervisor Network
        self.supervisor_network = SupervisorNetwork()
        
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
        execution_context: Optional[ExecutionContext] = None,
        reasoning_chain: Optional[List[ReasoningStep]] = None
    ) -> Dict[str, Any]:
        """
        Execute an action on behalf of an agent
        
        This is the main entry point for agent actions. It goes through
        the complete governance pipeline:
        1. Mute Agent validation (if configured)
        2. Permission check (Kernel)
        3. Constraint Graph validation (if enabled)
        4. Policy validation (Policy Engine)
        5. Risk assessment (Kernel)
        6. Rate limiting (Policy Engine)
        7. Shadow Mode or Real Execution
        8. Audit logging (Kernel)
        
        Args:
            agent_context: Context for the agent making the request
            action_type: Type of action to execute
            parameters: Parameters for the action
            execution_context: Optional execution context (sandboxing, timeouts, etc.)
            reasoning_chain: Optional reasoning steps that led to this action
            
        Returns:
            Dictionary with execution results and metadata
        """
        # 1. Validate against Mute Agent capabilities (if configured)
        if agent_context.agent_id in self.mute_validators:
            validator = self.mute_validators[agent_context.agent_id]
            # Create a temporary request for validation
            temp_request = ExecutionRequest(
                request_id="temp",
                agent_context=agent_context,
                action_type=action_type,
                parameters=parameters,
                timestamp=datetime.now()
            )
            is_valid, reason = validator.validate_request(temp_request)
            if not is_valid:
                return {
                    "success": False,
                    "error": reason,
                    "status": "capability_mismatch"
                }
        
        # 2. Submit request to kernel for permission check
        request = self.kernel.submit_request(agent_context, action_type, parameters)
        
        if request.status == ExecutionStatus.DENIED:
            return {
                "success": False,
                "error": "Request denied by kernel",
                "request_id": request.request_id,
                "status": request.status.value
            }
        
        # 3. Validate against Constraint Graphs (if enabled)
        if self.constraint_graphs_enabled and self.constraint_validator:
            is_valid, violations = self.constraint_validator.validate_request(request)
            if not is_valid:
                return {
                    "success": False,
                    "error": f"Constraint graph violations: {', '.join(violations)}",
                    "request_id": request.request_id,
                    "status": "constraint_violation",
                    "violations": violations
                }
        
        # 4. Validate with policy engine
        is_valid, reason = self.policy_engine.validate_request(request)
        if not is_valid:
            return {
                "success": False,
                "error": f"Policy validation failed: {reason}",
                "request_id": request.request_id,
                "status": "policy_violation"
            }
        
        # 5. Validate risk level
        if not self.policy_engine.validate_risk(request, request.risk_score):
            return {
                "success": False,
                "error": "Request risk level too high",
                "request_id": request.request_id,
                "risk_score": request.risk_score,
                "status": "risk_denied"
            }
        
        # 6. Execute in Shadow Mode or Real Mode
        if self.shadow_mode_enabled:
            # Shadow mode: simulate without executing
            simulation = self.shadow_executor.execute_in_shadow(request, reasoning_chain)
            return {
                "success": True,
                "result": simulation.simulated_result,
                "request_id": request.request_id,
                "status": "simulated",
                "outcome": simulation.outcome.value,
                "actual_impact": simulation.actual_impact,
                "risk_score": request.risk_score,
                "note": "This was executed in SHADOW MODE - no actual execution occurred"
            }
        else:
            # Real execution
            execution_result = self.execution_engine.execute(request, execution_context)
            
            # Update kernel with execution result
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
    
    # ===== New Methods for Advanced Features =====
    
    def enable_mute_agent(self, agent_id: str, config: MuteAgentConfig):
        """
        Enable Mute Agent mode for an agent.
        
        The agent will only execute actions that match its defined capabilities
        and return NULL for out-of-scope requests.
        """
        self.mute_validators[agent_id] = MuteAgentValidator(config)
    
    def enable_shadow_mode(self, enabled: bool = True):
        """
        Enable or disable shadow mode for all executions.
        
        In shadow mode, actions are simulated but not actually executed.
        """
        self.shadow_mode_enabled = enabled
        self.shadow_executor.config.enabled = enabled
    
    def get_shadow_simulations(self, agent_id: Optional[str] = None) -> List[Any]:
        """Get shadow mode simulation log"""
        return self.shadow_executor.get_simulation_log(agent_id)
    
    def get_shadow_statistics(self) -> Dict[str, Any]:
        """Get statistics about shadow mode executions"""
        return self.shadow_executor.get_statistics()
    
    def add_supervisor(self, supervisor: SupervisorAgent):
        """Add a supervisor agent to monitor worker agents"""
        self.supervisor_network.add_supervisor(supervisor)
    
    def run_supervision(self) -> Dict[str, List[Any]]:
        """
        Run a supervision cycle to check for violations.
        
        Returns violations detected by all supervisors.
        """
        execution_log = self.get_execution_history()
        audit_log = self.get_audit_log()
        return self.supervisor_network.run_supervision_cycle(execution_log, audit_log)
    
    def get_supervisor_summary(self) -> Dict[str, Any]:
        """Get summary of supervisor network activity"""
        return self.supervisor_network.get_network_summary()
    
    # Constraint Graph methods
    
    def add_data_table(self, table_name: str, schema: Dict[str, Any], metadata: Optional[Dict] = None):
        """Add a database table to the data graph"""
        if self.data_graph:
            self.data_graph.add_database_table(table_name, schema, metadata)
    
    def add_data_path(self, path: str, access_level: str = "read", metadata: Optional[Dict] = None):
        """Add a file path to the data graph"""
        if self.data_graph:
            self.data_graph.add_file_path(path, access_level, metadata)
    
    def add_policy_constraint(self, rule_id: str, name: str, applies_to: List[str], rule_type: str):
        """Add a policy constraint to the policy graph"""
        if self.policy_graph:
            self.policy_graph.add_policy_rule(rule_id, name, applies_to, rule_type)
    
    def add_maintenance_window(self, window_id: str, start_time, end_time, blocked_actions: List[ActionType]):
        """Add a maintenance window to the temporal graph"""
        if self.temporal_graph:
            self.temporal_graph.add_maintenance_window(window_id, start_time, end_time, blocked_actions)
    
    def get_constraint_validation_log(self) -> List[Dict[str, Any]]:
        """Get log of constraint graph validations"""
        if self.constraint_validator:
            return self.constraint_validator.get_validation_log()
        return []


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
