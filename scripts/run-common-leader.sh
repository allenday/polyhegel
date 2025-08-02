#!/bin/bash
"""
Start Polyhegel Common Analysis Leader Agent Server

Environment Variables:
  POLYHEGEL_COMMON_LEADER_HOST=0.0.0.0
  POLYHEGEL_COMMON_LEADER_PORT=7001
  POLYHEGEL_COMMON_LEADER_MODEL=claude-3-haiku-20240307
  POLYHEGEL_MAX_TECHNIQUES=3
"""

set -e

# Default configuration
export POLYHEGEL_COMMON_LEADER_HOST=${POLYHEGEL_COMMON_LEADER_HOST:-"0.0.0.0"}
export POLYHEGEL_COMMON_LEADER_PORT=${POLYHEGEL_COMMON_LEADER_PORT:-"7001"}
export POLYHEGEL_COMMON_LEADER_MODEL=${POLYHEGEL_COMMON_LEADER_MODEL:-"claude-3-haiku-20240307"}
export POLYHEGEL_MAX_TECHNIQUES=${POLYHEGEL_MAX_TECHNIQUES:-"3"}

echo "Starting Polyhegel Common Analysis Leader Agent..."
echo "Listening on ${POLYHEGEL_COMMON_LEADER_HOST}:${POLYHEGEL_COMMON_LEADER_PORT}"

cd "$(dirname "$0")/.."
python -m polyhegel.servers.common.common_analysis_leader_server