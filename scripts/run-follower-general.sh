#!/bin/bash
"""
Start Polyhegel Follower Agent (General - No Specialization)

Environment Variables:
  POLYHEGEL_FOLLOWER_HOST=0.0.0.0
  POLYHEGEL_FOLLOWER_PORT=8005
  POLYHEGEL_FOLLOWER_MODEL=claude-3-haiku-20240307
"""

set -e

# General follower (no specialization)
export POLYHEGEL_FOLLOWER_HOST=${POLYHEGEL_FOLLOWER_HOST:-"0.0.0.0"}
export POLYHEGEL_FOLLOWER_PORT=${POLYHEGEL_FOLLOWER_PORT:-"8005"}
export POLYHEGEL_FOLLOWER_MODEL=${POLYHEGEL_FOLLOWER_MODEL:-"claude-3-haiku-20240307"}
# No POLYHEGEL_SPECIALIZATION_DOMAIN = general agent

echo "Starting Polyhegel Follower Agent (General)..."
echo "Listening on ${POLYHEGEL_FOLLOWER_HOST}:${POLYHEGEL_FOLLOWER_PORT}"

cd "$(dirname "$0")/.."
python -m polyhegel.servers.follower_server