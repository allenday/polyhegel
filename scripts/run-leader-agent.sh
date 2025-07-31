#!/bin/bash
"""
Start Polyhegel Leader Agent Server

Environment Variables:
  POLYHEGEL_LEADER_HOST=0.0.0.0
  POLYHEGEL_LEADER_PORT=8001
  POLYHEGEL_LEADER_MODEL=claude-3-haiku-20240307
  POLYHEGEL_MAX_THEMES=5
  POLYHEGEL_FOCUS_DOMAINS=resource_acquisition,strategic_security,value_catalysis
"""

set -e

# Default configuration
export POLYHEGEL_LEADER_HOST=${POLYHEGEL_LEADER_HOST:-"0.0.0.0"}
export POLYHEGEL_LEADER_PORT=${POLYHEGEL_LEADER_PORT:-"8001"}
export POLYHEGEL_LEADER_MODEL=${POLYHEGEL_LEADER_MODEL:-"claude-3-haiku-20240307"}
export POLYHEGEL_MAX_THEMES=${POLYHEGEL_MAX_THEMES:-"5"}

echo "Starting Polyhegel Leader Agent..."
echo "Listening on ${POLYHEGEL_LEADER_HOST}:${POLYHEGEL_LEADER_PORT}"

cd "$(dirname "$0")/.."
python -m polyhegel.servers.leader_server