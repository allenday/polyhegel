#!/bin/bash
"""
Start All Polyhegel Common Cross-Domain Agents

Starts the common analysis leader and all follower agents for common techniques:
- Common Analysis Leader (port 7001)
- Stakeholder Analysis Follower (port 7002)
- Trade-off Analysis Follower (port 7003)
- Risk Assessment Follower (port 7004)
- Consensus Building Follower (port 7005)
- Scenario Planning Follower (port 7006)

Environment Variables:
  POLYHEGEL_MODEL=claude-3-haiku-20240307
  POLYHEGEL_HOST=0.0.0.0
"""

set -e

# Default configuration
export POLYHEGEL_MODEL=${POLYHEGEL_MODEL:-"claude-3-haiku-20240307"}
export POLYHEGEL_HOST=${POLYHEGEL_HOST:-"0.0.0.0"}

# Set model for all agents
export POLYHEGEL_COMMON_LEADER_MODEL=${POLYHEGEL_MODEL}
export POLYHEGEL_FOLLOWER_MODEL=${POLYHEGEL_MODEL}

# Set host for all agents
export POLYHEGEL_COMMON_LEADER_HOST=${POLYHEGEL_HOST}
export POLYHEGEL_FOLLOWER_HOST=${POLYHEGEL_HOST}

echo "Starting all Polyhegel Common Cross-Domain Agents..."
echo "Model: ${POLYHEGEL_MODEL}"
echo "Host: ${POLYHEGEL_HOST}"
echo ""

SCRIPT_DIR="$(dirname "$0")"

# Function to start agent in background
start_agent() {
    local script_name=$1
    local agent_name=$2
    echo "Starting ${agent_name}..."
    "${SCRIPT_DIR}/${script_name}" &
    sleep 2  # Give each agent time to start
}

# Start all agents
start_agent "run-common-leader.sh" "Common Analysis Leader"
start_agent "run-common-follower-stakeholder.sh" "Stakeholder Analysis Follower"
start_agent "run-common-follower-tradeoff.sh" "Trade-off Analysis Follower"
start_agent "run-common-follower-risk.sh" "Risk Assessment Follower"
start_agent "run-common-follower-consensus.sh" "Consensus Building Follower"
start_agent "run-common-follower-scenario.sh" "Scenario Planning Follower"

echo ""
echo "All common agents started!"
echo ""
echo "Ports:"
echo "  Common Analysis Leader:        http://${POLYHEGEL_HOST}:7001"
echo "  Stakeholder Analysis Follower: http://${POLYHEGEL_HOST}:7002"
echo "  Trade-off Analysis Follower:   http://${POLYHEGEL_HOST}:7003"
echo "  Risk Assessment Follower:      http://${POLYHEGEL_HOST}:7004"
echo "  Consensus Building Follower:   http://${POLYHEGEL_HOST}:7005"
echo "  Scenario Planning Follower:    http://${POLYHEGEL_HOST}:7006"
echo ""
echo "Press Ctrl+C to stop all agents"

# Wait for all background processes
wait