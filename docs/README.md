# Agent Control Plane Documentation

Welcome to the Agent Control Plane documentation! This comprehensive guide will help you understand, use, and contribute to the Agent Control Plane.

## Table of Contents

### Getting Started
- [Quick Start Guide](guides/QUICKSTART.md) - Get up and running in 5 minutes
- [Installation](guides/INSTALLATION.md) - Detailed installation instructions

### Guides
- [Quick Start](guides/QUICKSTART.md) - Getting started with Agent Control Plane
- [Implementation Guide](guides/IMPLEMENTATION.md) - Implementation details and best practices
- [Philosophy](guides/PHILOSOPHY.md) - Core principles and design philosophy

### Architecture
- [Architecture Overview](architecture/architecture.md) - System architecture and components
- [Core Components](architecture/COMPONENTS.md) - Detailed component documentation
- [Design Patterns](architecture/PATTERNS.md) - Common patterns and practices

### API Reference
- [Core API](api/CORE.md) - Main API reference
- [Policy Engine](api/POLICY.md) - Policy engine API
- [Execution Engine](api/EXECUTION.md) - Execution engine API
- [Advanced Features](api/ADVANCED.md) - Advanced features API

### Examples
See the [examples directory](../examples/) for working code examples:
- Basic Usage - Fundamental concepts
- Advanced Features - Mute Agent, Shadow Mode, etc.
- Configuration - Different agent profiles

### Contributing
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute to the project

## What is Agent Control Plane?

Agent Control Plane is a governance and management layer for autonomous AI agents. It treats the LLM as a raw compute component and provides a kernel-like layer for safe, controlled execution.

## Key Features

### Core Features
- **Permission Management**: Fine-grained control over what agents can do
- **Policy Enforcement**: Governance rules and compliance constraints
- **Resource Management**: Quotas, rate limiting, and resource allocation
- **Safe Execution**: Sandboxed execution with rollback capability
- **Audit Logging**: Complete traceability for all agent actions
- **Risk Assessment**: Automatic risk scoring and management

### Advanced Features
- **The Mute Agent**: Capability-based execution that returns NULL for out-of-scope requests
- **Shadow Mode**: Simulation environment for validating agent behavior
- **Constraint Graphs**: Multi-dimensional context (Data, Policy, Temporal)
- **Supervisor Agents**: Recursive governance with agents watching agents
- **Reasoning Telemetry**: Complete trace of agent decision-making

## Quick Links

- [GitHub Repository](https://github.com/imran-siddique/agent-control-plane)
- [Issue Tracker](https://github.com/imran-siddique/agent-control-plane/issues)
- [Contributing Guidelines](../CONTRIBUTING.md)

## Philosophy: Scale by Subtraction

We need to stop treating the LLM as a magic box and start treating it as a raw compute component that requires a kernel.

In distributed systems, we don't ask a microservice nicely to respect a rate limit—we enforce it at the gateway. We don't ask a database query nicely not to drop a table—we enforce it via permissions. With AI agents, we need the same deterministic enforcement.

## Getting Help

- Read the [Quick Start Guide](guides/QUICKSTART.md)
- Check the [examples directory](../examples/)
- Look at existing [tests](../tests/)
- Open an [issue](https://github.com/imran-siddique/agent-control-plane/issues) on GitHub

## License

This project is licensed under the MIT License - see the LICENSE file for details.
