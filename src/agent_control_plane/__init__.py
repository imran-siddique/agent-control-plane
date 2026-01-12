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
    Condition,
    ConditionalPermission,
    create_default_policies,
)

from .flight_recorder import (
    FlightRecorder,
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

from .adapter import (
    ControlPlaneAdapter,
    create_governed_client,
    DEFAULT_TOOL_MAPPING,
)

__version__ = "0.1.0"
__author__ = "Agent Control Plane Contributors"

__all__ = [
    # Main interface
    "AgentControlPlane",
    "create_read_only_agent",
    "create_standard_agent",
    "create_admin_agent",
    
    # Adapter (Drop-in Middleware)
    "ControlPlaneAdapter",
    "create_governed_client",
    "DEFAULT_TOOL_MAPPING",
    
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
    "Condition",
    "ConditionalPermission",
    "create_default_policies",
    
    # Audit
    "FlightRecorder",
    
    # Execution
    "ExecutionEngine",
    "ExecutionContext",
    "ExecutionMetrics",
]
