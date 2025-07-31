#!/bin/bash
"""
Start Polyhegel Follower Agent (Value Catalysis Specialization)

Environment Variables:
  POLYHEGEL_FOLLOWER_HOST=0.0.0.0
  POLYHEGEL_FOLLOWER_PORT=8004
  POLYHEGEL_FOLLOWER_MODEL=claude-3-haiku-20240307
"""

set -e

# Value catalysis specialization
export POLYHEGEL_FOLLOWER_HOST=${POLYHEGEL_FOLLOWER_HOST:-"0.0.0.0"}
export POLYHEGEL_FOLLOWER_PORT=${POLYHEGEL_FOLLOWER_PORT:-"8004"}
export POLYHEGEL_FOLLOWER_MODEL=${POLYHEGEL_FOLLOWER_MODEL:-"claude-3-haiku-20240307"}
export POLYHEGEL_SPECIALIZATION_DOMAIN="value_catalysis"

echo "Starting Polyhegel Follower Agent (Value Catalysis)..."
echo "Listening on ${POLYHEGEL_FOLLOWER_HOST}:${POLYHEGEL_FOLLOWER_PORT}"

cd "$(dirname "$0")/.."
python -m polyhegel.servers.follower_server