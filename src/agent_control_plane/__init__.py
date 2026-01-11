"""
Agent Control Plane

A governance and management layer for autonomous AI agents.
"""

from .agent_kernel import (
    AgentKernel,
    AgentContext,
    ExecutionRequest,
    ExecutionResult,
    ActionType,
    PermissionLevel,
    ExecutionStatus,
    PolicyRule,
)

from .policy_engine import (
    PolicyEngine,
    ResourceQuota,
    RiskPolicy,
    create_default_policies,
)

from .execution_engine import (
    ExecutionEngine,
    ExecutionContext,
    SandboxLevel,
    ExecutionMetrics,
)

from .control_plane import (
    AgentControlPlane,
    create_read_only_agent,
    create_standard_agent,
    create_admin_agent,
)

__version__ = "0.1.0"
__author__ = "Agent Control Plane Contributors"

__all__ = [
    # Main interface
    "AgentControlPlane",
    "create_read_only_agent",
    "create_standard_agent",
    "create_admin_agent",
    
    # Kernel
    "AgentKernel",
    "AgentContext",
    "ExecutionRequest",
    "ExecutionResult",
    "PolicyRule",
    
    # Enums
    "ActionType",
    "PermissionLevel",
    "ExecutionStatus",
    "SandboxLevel",
    
    # Policy
    "PolicyEngine",
    "ResourceQuota",
    "RiskPolicy",
    "create_default_policies",
    
    # Execution
    "ExecutionEngine",
    "ExecutionContext",
    "ExecutionMetrics",
]
