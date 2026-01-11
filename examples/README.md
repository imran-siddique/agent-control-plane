# Examples

This directory contains example scripts demonstrating how to use Agent Control Plane.

## Available Examples

### Basic Usage (`basic_usage.py`)
Demonstrates fundamental concepts and basic usage patterns:
- Creating the control plane
- Creating agents with different permission levels
- Executing actions
- Handling permissions and errors

Run:
```bash
python examples/basic_usage.py
```

### Advanced Features (`advanced_features.py`)
Showcases advanced capabilities:
- Mute Agent - Capability-based execution
- Shadow Mode - Simulation without execution
- Constraint Graphs - Multi-dimensional context
- Supervisor Agents - Recursive governance
- Reasoning Telemetry - Tracking agent decisions

Run:
```bash
python examples/advanced_features.py
```

### Configuration (`configuration.py`)
Shows different configuration patterns and agent profiles:
- Development/Testing agent configuration
- Production agent configuration
- Read-only agent configuration
- Multi-tenant configurations

Run:
```bash
python examples/configuration.py
```

## Creating Your Own Examples

When creating examples:
1. Import from `agent_control_plane` package
2. Include clear comments explaining each step
3. Use descriptive variable names
4. Show both success and error cases
5. Keep examples focused on specific features

Example template:
```python
"""
Example: Your Feature Name

This example demonstrates how to use [feature name].
"""

from agent_control_plane import AgentControlPlane, create_standard_agent
from agent_control_plane.agent_kernel import ActionType

def example_function():
    """Demonstrates [specific functionality]"""
    # Create control plane
    control_plane = AgentControlPlane()
    
    # Your example code here
    pass

if __name__ == "__main__":
    example_function()
```
