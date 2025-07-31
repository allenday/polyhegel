#!/bin/bash
"""
Start All Polyhegel A2A Agent Servers

Launches a complete distributed A2A agent ecosystem:
- Leader Agent (port 8001)
- Resource Acquisition Follower (port 8002)  
- Strategic Security Follower (port 8003)
- Value Catalysis Follower (port 8004)
- General Follower (port 8005)

Usage:
  ./scripts/run-all-agents.sh        # Start all agents
  ./scripts/run-all-agents.sh stop   # Stop all agents
"""

set -e

SCRIPT_DIR="$(dirname "$0")"
PID_DIR="/tmp/polyhegel-agents"

# Create PID directory
mkdir -p "$PID_DIR"

start_agents() {
    echo "🚀 Starting Polyhegel A2A Agent Ecosystem..."
    
    # Start Leader Agent
    echo "Starting Leader Agent (port 8001)..."
    POLYHEGEL_LEADER_PORT=8001 nohup "$SCRIPT_DIR/run-leader-agent.sh" > "$PID_DIR/leader.log" 2>&1 & 
    echo $! > "$PID_DIR/leader.pid"
    
    # Start Resource Follower
    echo "Starting Resource Acquisition Follower (port 8002)..."
    POLYHEGEL_FOLLOWER_PORT=8002 nohup "$SCRIPT_DIR/run-follower-resource.sh" > "$PID_DIR/resource.log" 2>&1 &
    echo $! > "$PID_DIR/resource.pid"
    
    # Start Security Follower  
    echo "Starting Strategic Security Follower (port 8003)..."
    POLYHEGEL_FOLLOWER_PORT=8003 nohup "$SCRIPT_DIR/run-follower-security.sh" > "$PID_DIR/security.log" 2>&1 &
    echo $! > "$PID_DIR/security.pid"
    
    # Start Value Follower
    echo "Starting Value Catalysis Follower (port 8004)..."
    POLYHEGEL_FOLLOWER_PORT=8004 nohup "$SCRIPT_DIR/run-follower-value.sh" > "$PID_DIR/value.log" 2>&1 &
    echo $! > "$PID_DIR/value.pid"
    
    # Start General Follower
    echo "Starting General Follower (port 8005)..."
    POLYHEGEL_FOLLOWER_PORT=8005 nohup "$SCRIPT_DIR/run-follower-general.sh" > "$PID_DIR/general.log" 2>&1 &
    echo $! > "$PID_DIR/general.pid"
    
    sleep 3
    
    echo ""
    echo "✅ Polyhegel A2A Agent Ecosystem Started!"
    echo ""
    echo "Agent Endpoints:"
    echo "  Leader:               http://localhost:8001"
    echo "  Resource Acquisition: http://localhost:8002"  
    echo "  Strategic Security:   http://localhost:8003"
    echo "  Value Catalysis:      http://localhost:8004"
    echo "  General:              http://localhost:8005"
    echo ""
    echo "Logs: $PID_DIR/*.log"
    echo "PIDs: $PID_DIR/*.pid"
    echo ""
    echo "To stop: $0 stop"
}

stop_agents() {
    echo "🛑 Stopping Polyhegel A2A Agent Ecosystem..."
    
    for service in leader resource security value general; do
        pid_file="$PID_DIR/$service.pid"
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                echo "Stopping $service agent (PID $pid)..."
                kill "$pid"
                rm "$pid_file"
            else
                echo "$service agent not running"
                rm -f "$pid_file"
            fi
        else
            echo "$service agent PID file not found"
        fi
    done
    
    echo "✅ All agents stopped"
}

check_status() {
    echo "📊 Polyhegel A2A Agent Status:"
    echo ""
    
    for service in leader resource security value general; do
        pid_file="$PID_DIR/$service.pid"
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                echo "✅ $service agent: Running (PID $pid)"
            else
                echo "❌ $service agent: Stopped (stale PID file)"
            fi
        else
            echo "❌ $service agent: Stopped"
        fi
    done
    echo ""
}

case "${1:-start}" in
    start)
        start_agents
        ;;
    stop)
        stop_agents
        ;;
    status)
        check_status
        ;;
    restart)
        stop_agents
        sleep 2
        start_agents
        ;;
    *)
        echo "Usage: $0 [start|stop|status|restart]"
        exit 1
        ;;
esac