#!/bin/bash
"""
Start Polyhegel Technical Architecture Follower Agent (Backend Architecture Specialization)

Environment Variables:
  POLYHEGEL_TECHARCH_FOLLOWER_HOST=0.0.0.0
  POLYHEGEL_TECHARCH_FOLLOWER_PORT=9002
  POLYHEGEL_TECHARCH_FOLLOWER_MODEL=claude-3-haiku-20240307
"""

set -e

# Backend architecture specialization
export POLYHEGEL_TECHARCH_FOLLOWER_HOST=${POLYHEGEL_TECHARCH_FOLLOWER_HOST:-"0.0.0.0"}
export POLYHEGEL_TECHARCH_FOLLOWER_PORT=${POLYHEGEL_TECHARCH_FOLLOWER_PORT:-"9002"}
export POLYHEGEL_TECHARCH_FOLLOWER_MODEL=${POLYHEGEL_TECHARCH_FOLLOWER_MODEL:-"claude-3-haiku-20240307"}
export POLYHEGEL_TECHARCH_SPECIALIZATION_DOMAIN="backend_architecture"

echo "Starting Polyhegel Technical Architecture Follower Agent (Backend Architecture)..."
echo "Listening on ${POLYHEGEL_TECHARCH_FOLLOWER_HOST}:${POLYHEGEL_TECHARCH_FOLLOWER_PORT}"

cd "$(dirname "$0")/.."
python -m polyhegel.servers.technical_architecture_follower_server