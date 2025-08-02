#!/bin/bash
"""
Start Polyhegel Technical Architecture Leader Agent Server

Environment Variables:
  POLYHEGEL_TECHARCH_LEADER_HOST=0.0.0.0
  POLYHEGEL_TECHARCH_LEADER_PORT=9001
  POLYHEGEL_TECHARCH_LEADER_MODEL=claude-3-haiku-20240307
  POLYHEGEL_TECHARCH_COMPLEXITY_TOLERANCE=medium
  POLYHEGEL_TECHARCH_FOCUS_DOMAINS=backend_architecture,frontend_architecture,infrastructure_architecture,security_architecture
"""

set -e

# Default configuration
export POLYHEGEL_TECHARCH_LEADER_HOST=${POLYHEGEL_TECHARCH_LEADER_HOST:-"0.0.0.0"}
export POLYHEGEL_TECHARCH_LEADER_PORT=${POLYHEGEL_TECHARCH_LEADER_PORT:-"9001"}
export POLYHEGEL_TECHARCH_LEADER_MODEL=${POLYHEGEL_TECHARCH_LEADER_MODEL:-"claude-3-haiku-20240307"}
export POLYHEGEL_TECHARCH_COMPLEXITY_TOLERANCE=${POLYHEGEL_TECHARCH_COMPLEXITY_TOLERANCE:-"medium"}

echo "Starting Polyhegel Technical Architecture Leader Agent..."
echo "Listening on ${POLYHEGEL_TECHARCH_LEADER_HOST}:${POLYHEGEL_TECHARCH_LEADER_PORT}"
echo "Complexity Tolerance: ${POLYHEGEL_TECHARCH_COMPLEXITY_TOLERANCE}"

cd "$(dirname "$0")/.."
python -m polyhegel.servers.technical_architecture_leader_server