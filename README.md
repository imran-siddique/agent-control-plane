# Agent Control Plane

A governance and management layer for autonomous AI agents. The Agent Control Plane treats the LLM as a raw compute component and provides a kernel-like layer for safe, controlled execution.

## Overview

As we move from chatbots to autonomous agents—systems that can execute code, modify data, and trigger workflows—the biggest bottleneck isn't intelligence. It's governance. The Agent Control Plane solves this by providing:

- **Permission Management**: Fine-grained control over what agents can do
- **Policy Enforcement**: Governance rules and compliance constraints
- **Resource Management**: Quotas, rate limiting, and resource allocation
- **Safe Execution**: Sandboxed execution with rollback capability
- **Audit Logging**: Complete traceability for all agent actions
- **Risk Assessment**: Automatic risk scoring and management

## Key Concepts

### The Problem

Traditional LLM applications lack proper governance:
- Agents have unrestricted access to execute dangerous actions
- No rate limiting or resource quotas
- Limited visibility into agent behavior
- Difficult to enforce compliance requirements
- Hard to debug and trace agent decisions

### The Solution

The Agent Control Plane sits between the LLM (raw compute) and the execution environment, providing:

1. **Agent Kernel**: Central coordinator that mediates all agent actions
2. **Policy Engine**: Enforces rules and constraints
3. **Execution Engine**: Safely executes actions in sandboxed environments
4. **Audit System**: Tracks all activities for compliance and debugging

## Quick Start

### Basic Usage

```python
from control_plane import AgentControlPlane, create_standard_agent
from agent_kernel import ActionType

# Create the control plane
control_plane = AgentControlPlane()

# Create an agent with standard permissions
agent = create_standard_agent(control_plane, "my-agent")

# Execute an action
result = control_plane.execute_action(
    agent,
    ActionType.FILE_READ,
    {"path": "/data/myfile.txt"}
)

if result["success"]:
    print(f"Result: {result['result']}")
else:
    print(f"Error: {result['error']}")
```

### Permission Control

```python
from agent_kernel import ActionType, PermissionLevel

# Create custom permissions
permissions = {
    ActionType.FILE_READ: PermissionLevel.READ_ONLY,
    ActionType.API_CALL: PermissionLevel.READ_WRITE,
    ActionType.CODE_EXECUTION: PermissionLevel.NONE,
}

agent = control_plane.create_agent("restricted-agent", permissions)
```

### Rate Limiting

```python
from policy_engine import ResourceQuota

# Set strict quotas
quota = ResourceQuota(
    agent_id="rate-limited-agent",
    max_requests_per_minute=10,
    max_requests_per_hour=100,
    max_concurrent_executions=2,
)

agent = control_plane.create_agent("rate-limited-agent", quota=quota)
```

### Custom Policies

```python
from agent_kernel import PolicyRule
import uuid

def validate_safe_path(request):
    """Only allow access to /data directory"""
    path = request.parameters.get('path', '')
    return path.startswith('/data/')

rule = PolicyRule(
    rule_id=str(uuid.uuid4()),
    name="safe_path_only",
    description="Restrict file access to /data directory",
    action_types=[ActionType.FILE_READ, ActionType.FILE_WRITE],
    validator=validate_safe_path,
    priority=10
)

control_plane.add_policy_rule(rule)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Application Layer                     │
│                    (Chat, Workflow, Tools)                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      Agent Control Plane                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Agent     │  │   Policy     │  │   Audit      │      │
│  │   Kernel     │◄─┤   Engine     │◄─┤   Logger     │      │
│  └──────┬───────┘  └──────────────┘  └──────────────┘      │
│         │                                                     │
│  ┌──────▼───────┐  ┌──────────────┐                         │
│  │  Resource    │  │  Execution   │                         │
│  │   Manager    │◄─┤   Engine     │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    LLM (Raw Compute)                         │
│              (GPT-4, Claude, Llama, etc.)                    │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Execution Environment                       │
│         (Code, Databases, APIs, File System)                 │
└─────────────────────────────────────────────────────────────┘
```

## Components

### Agent Kernel
The kernel mediates all interactions between the LLM and execution environment:
- Permission checking
- Request validation
- Risk assessment
- Audit logging

### Policy Engine
Enforces governance rules:
- Rate limiting and quotas
- Custom policy rules
- Risk management
- Access control

### Execution Engine
Safely executes agent actions:
- Sandboxed environments
- Timeout enforcement
- Resource monitoring
- Error handling

## Examples

Run the examples to see the control plane in action:

```bash
python3 examples.py
```

This demonstrates:
- Basic usage
- Permission control
- Rate limiting
- Policy enforcement
- Audit logging
- Risk management

## Testing

Run the test suite:

```bash
python3 test_control_plane.py
```

## Use Cases

### Enterprise AI Agents
Deploy agents with strict governance for enterprise environments:
- Compliance with security policies
- Audit trails for regulatory requirements
- Resource quotas to control costs

### Multi-tenant AI Platforms
Safely run multiple agents with isolation:
- Per-tenant quotas and policies
- Isolated execution environments
- Fair resource allocation

### Development & Testing
Experiment safely with agent capabilities:
- Sandboxed execution
- Easy rollback of changes
- Comprehensive logging

### Production Workflows
Run reliable, auditable agent workflows:
- Error handling and recovery
- Performance monitoring
- Traceability for debugging

## API Reference

See [architecture.md](architecture.md) for detailed architecture documentation.

### Core Classes

- `AgentControlPlane`: Main control plane interface
- `AgentKernel`: Core kernel component
- `PolicyEngine`: Policy enforcement
- `ExecutionEngine`: Safe execution
- `AgentContext`: Agent session context
- `ExecutionRequest`: Action request
- `ExecutionResult`: Action result

### Action Types

- `FILE_READ`: Read file operations
- `FILE_WRITE`: Write file operations
- `CODE_EXECUTION`: Execute code
- `API_CALL`: Make API calls
- `DATABASE_QUERY`: Query databases
- `DATABASE_WRITE`: Write to databases
- `WORKFLOW_TRIGGER`: Trigger workflows

### Permission Levels

- `NONE`: No access
- `READ_ONLY`: Read-only access
- `READ_WRITE`: Read and write access
- `ADMIN`: Full administrative access

## Best Practices

1. **Start with minimal permissions**: Grant only what's needed
2. **Use rate limits**: Prevent runaway agents
3. **Enable audit logging**: Track all agent actions
4. **Test policies**: Validate governance rules work as expected
5. **Monitor resource usage**: Watch for anomalies
6. **Regular policy reviews**: Keep policies up to date

## Security Considerations

- Default policies block system file access
- Credentials should never be in parameters
- High-risk actions require elevated permissions
- All actions are audited
- Sandboxed execution by default

## Future Enhancements

- [ ] Distributed execution across multiple nodes
- [ ] Integration with external policy engines (OPA, etc.)
- [ ] Real-time monitoring dashboard
- [ ] Machine learning-based risk assessment
- [ ] Automatic policy generation from past behavior
- [ ] Integration with secrets management systems
- [ ] Container-based sandboxing
- [ ] Transaction rollback for database operations

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

MIT License - See LICENSE file for details