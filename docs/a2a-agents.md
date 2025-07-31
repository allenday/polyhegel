# Polyhegel A2A Agent Servers

Polyhegel agents can run as standalone A2A (Agent-to-Agent) protocol servers for distributed strategic simulation.

## Quick Start

```bash
# Start all agents
make agents-start

# Check status  
make agents-status

# Stop all agents
make agents-stop
```

## Architecture

The A2A agent ecosystem consists of:

- **Leader Agent** (port 8001): Generates strategic themes
- **Resource Follower** (port 8002): Specializes in resource acquisition strategies  
- **Security Follower** (port 8003): Specializes in strategic security strategies
- **Value Follower** (port 8004): Specializes in value catalysis strategies
- **General Follower** (port 8005): General-purpose strategy development

## Individual Agent Scripts

```bash
# Start individual agents
./scripts/run-leader-agent.sh
./scripts/run-follower-resource.sh  
./scripts/run-follower-security.sh
./scripts/run-follower-value.sh
./scripts/run-follower-general.sh
```

## Configuration

Configure via environment variables:

```bash
# Leader Agent
export POLYHEGEL_LEADER_HOST=0.0.0.0
export POLYHEGEL_LEADER_PORT=8001  
export POLYHEGEL_LEADER_MODEL=claude-3-haiku-20240307
export POLYHEGEL_MAX_THEMES=5
export POLYHEGEL_FOCUS_DOMAINS=resource_acquisition,strategic_security

# Follower Agents
export POLYHEGEL_FOLLOWER_HOST=0.0.0.0
export POLYHEGEL_FOLLOWER_PORT=8002
export POLYHEGEL_FOLLOWER_MODEL=claude-3-haiku-20240307
export POLYHEGEL_SPECIALIZATION_DOMAIN=resource_acquisition
```

## A2A Protocol Integration

Each agent exposes:
- **Agent Card**: `/agent_card` - Agent capabilities and skills
- **Task Endpoint**: `/tasks` - Submit strategy generation tasks
- **Streaming**: Real-time progress updates via A2A protocol

## Usage with Polyhegel CLI

The CLI automatically uses A2A agents when in hierarchical mode:

```bash
# Uses distributed A2A agents
python -m polyhegel simulate \
  --output results/ \
  --mode hierarchical \
  --user-prompt-file challenge.md
```

Environment variables configure endpoints:
```bash
export POLYHEGEL_LEADER_URL=http://localhost:8001
export POLYHEGEL_FOLLOWER_RESOURCE_URL=http://localhost:8002
export POLYHEGEL_FOLLOWER_SECURITY_URL=http://localhost:8003
export POLYHEGEL_FOLLOWER_VALUE_URL=http://localhost:8004
export POLYHEGEL_FOLLOWER_GENERAL_URL=http://localhost:8005
```