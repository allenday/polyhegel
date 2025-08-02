#!/bin/bash
"""
Start Polyhegel Scenario Planning Follower Agent Server

Environment Variables:
  POLYHEGEL_FOLLOWER_HOST=0.0.0.0
  POLYHEGEL_FOLLOWER_PORT=7006
  POLYHEGEL_FOLLOWER_MODEL=claude-3-haiku-20240307
"""

set -e

# Default configuration
export POLYHEGEL_FOLLOWER_HOST=${POLYHEGEL_FOLLOWER_HOST:-"0.0.0.0"}
export POLYHEGEL_FOLLOWER_PORT=${POLYHEGEL_FOLLOWER_PORT:-"7006"}
export POLYHEGEL_FOLLOWER_MODEL=${POLYHEGEL_FOLLOWER_MODEL:-"claude-3-haiku-20240307"}
export POLYHEGEL_FOLLOWER_TYPE="scenario"

echo "Starting Polyhegel Scenario Planning Follower Agent..."
echo "Listening on ${POLYHEGEL_FOLLOWER_HOST}:${POLYHEGEL_FOLLOWER_PORT}"

cd "$(dirname "$0")/.."
python -m polyhegel.servers.common.common_follower_server scenario