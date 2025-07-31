#!/bin/bash
"""
Start Polyhegel Follower Agent (Strategic Security Specialization)

Environment Variables:
  POLYHEGEL_FOLLOWER_HOST=0.0.0.0
  POLYHEGEL_FOLLOWER_PORT=8003
  POLYHEGEL_FOLLOWER_MODEL=claude-3-haiku-20240307
"""

set -e

# Strategic security specialization
export POLYHEGEL_FOLLOWER_HOST=${POLYHEGEL_FOLLOWER_HOST:-"0.0.0.0"}
export POLYHEGEL_FOLLOWER_PORT=${POLYHEGEL_FOLLOWER_PORT:-"8003"}
export POLYHEGEL_FOLLOWER_MODEL=${POLYHEGEL_FOLLOWER_MODEL:-"claude-3-haiku-20240307"}
export POLYHEGEL_SPECIALIZATION_DOMAIN="strategic_security"

echo "Starting Polyhegel Follower Agent (Strategic Security)..."
echo "Listening on ${POLYHEGEL_FOLLOWER_HOST}:${POLYHEGEL_FOLLOWER_PORT}"

cd "$(dirname "$0")/.."
python -m polyhegel.servers.follower_server