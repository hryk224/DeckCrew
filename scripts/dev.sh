#!/usr/bin/env bash
set -euo pipefail

# Dev server management for DeckCrew.
# Usage:
#   scripts/dev.sh start     Start frontend + backend
#   scripts/dev.sh stop      Stop via recorded PIDs
#   scripts/dev.sh restart   Stop then start
#   scripts/dev.sh preview <name>  Print preview URL
#   scripts/dev.sh status    Show running state

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_DIR="$ROOT_DIR/.dev-pids"
FE_PID_FILE="$PID_DIR/frontend.pid"
BE_PID_FILE="$PID_DIR/backend.pid"
FE_PORT=3000
BE_PORT=8000

_ensure_pid_dir() {
  mkdir -p "$PID_DIR"
}

_is_running() {
  local pid_file="$1"
  if [ -f "$pid_file" ]; then
    local pid
    pid=$(cat "$pid_file")
    if kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
  fi
  return 1
}

_stop_pid() {
  local name="$1" pid_file="$2" port="$3"

  if [ ! -f "$pid_file" ]; then
    echo "$name: no pidfile"
    return
  fi

  local pid
  pid=$(cat "$pid_file")

  if kill -0 "$pid" 2>/dev/null; then
    echo "$name: stopping PID $pid"
    # Kill the process group to catch child processes
    kill -- -"$pid" 2>/dev/null || kill "$pid" 2>/dev/null || true
    # Wait up to 5 seconds for port to free
    for _ in $(seq 1 10); do
      if ! lsof -i :"$port" -t >/dev/null 2>&1; then
        break
      fi
      sleep 0.5
    done
  else
    echo "$name: PID $pid not running"
  fi

  rm -f "$pid_file"

  # Verify port is free
  if lsof -i :"$port" -t >/dev/null 2>&1; then
    echo "$name: WARNING - port $port still in use after stop"
    echo "  Manual cleanup: lsof -i :$port -t | xargs kill"
  else
    echo "$name: port $port free"
  fi
}

cmd_start() {
  _ensure_pid_dir

  # Check for already running
  if _is_running "$FE_PID_FILE"; then
    echo "Frontend already running (PID $(cat "$FE_PID_FILE"))"
  else
    echo "Starting frontend on port $FE_PORT..."
    cd "$ROOT_DIR/frontend"
    setsid npm run dev > "$PID_DIR/frontend.log" 2>&1 &
    local fe_pid=$!
    echo "$fe_pid" > "$FE_PID_FILE"
    echo "Frontend PID: $fe_pid (log: .dev-pids/frontend.log)"
  fi

  if _is_running "$BE_PID_FILE"; then
    echo "Backend already running (PID $(cat "$BE_PID_FILE"))"
  else
    echo "Starting backend on port $BE_PORT..."
    cd "$ROOT_DIR/backend"
    local env_file="$ROOT_DIR/.env"
    local env_flag=""
    if [ -f "$env_file" ]; then
      env_flag="--env-file $env_file"
    fi
    setsid env DEBUG=1 uv run uvicorn deckcrew.main:app --reload --port "$BE_PORT" $env_flag \
      > "$PID_DIR/backend.log" 2>&1 &
    local be_pid=$!
    echo "$be_pid" > "$BE_PID_FILE"
    echo "Backend PID: $be_pid (log: .dev-pids/backend.log)"
  fi

  # Wait for servers to be ready
  echo ""
  echo "Waiting for servers..."
  local ready=0
  for i in $(seq 1 20); do
    sleep 2
    local fe_ok=0 be_ok=0
    curl --max-time 3 -s -o /dev/null http://localhost:$FE_PORT/ 2>/dev/null && fe_ok=1
    curl --max-time 3 -s -o /dev/null http://localhost:$BE_PORT/health 2>/dev/null && be_ok=1
    if [ "$fe_ok" = "1" ] && [ "$be_ok" = "1" ]; then
      ready=1
      break
    fi
    printf "  [%2d] frontend=%s backend=%s\n" "$i" \
      "$([ "$fe_ok" = "1" ] && echo "ready" || echo "...")" \
      "$([ "$be_ok" = "1" ] && echo "ready" || echo "...")"
  done

  echo ""
  if [ "$ready" = "1" ]; then
    echo "Both servers ready."
    echo "  Frontend: http://localhost:$FE_PORT/"
    echo "  Backend:  http://localhost:$BE_PORT/health"
  else
    echo "WARNING: Servers did not become ready in time."
    echo "  Check logs: .dev-pids/frontend.log, .dev-pids/backend.log"
  fi
}

cmd_stop() {
  _stop_pid "Frontend" "$FE_PID_FILE" "$FE_PORT"
  _stop_pid "Backend" "$BE_PID_FILE" "$BE_PORT"
}

cmd_restart() {
  cmd_stop
  echo ""
  cmd_start
}

cmd_preview() {
  local scenario="${1:-}"
  local snapshots="idle build-major peak-with-feedback crowd-requested-shift"
  local timelines="timeline-house-party timeline-chill-lounge timeline-open-format-debate"

  if [ -z "$scenario" ]; then
    echo "Usage: scripts/dev.sh preview <scenario>"
    echo ""
    echo "Snapshots (single state):"
    for s in $snapshots; do
      echo "  $s  ->  http://localhost:$FE_PORT/?preview=$s"
    done
    echo ""
    echo "Timelines (multi-turn experience):"
    for s in $timelines; do
      echo "  $s  ->  http://localhost:$FE_PORT/?preview=$s"
    done
    return
  fi

  echo "Preview URL:"
  echo "  http://localhost:$FE_PORT/?preview=$scenario"
}

cmd_status() {
  echo "Frontend:"
  if _is_running "$FE_PID_FILE"; then
    echo "  Running (PID $(cat "$FE_PID_FILE"), port $FE_PORT)"
  else
    echo "  Not running"
  fi

  echo "Backend:"
  if _is_running "$BE_PID_FILE"; then
    echo "  Running (PID $(cat "$BE_PID_FILE"), port $BE_PORT)"
  else
    echo "  Not running"
  fi
}

case "${1:-}" in
  start)   cmd_start ;;
  stop)    cmd_stop ;;
  restart) cmd_restart ;;
  preview) cmd_preview "${2:-}" ;;
  status)  cmd_status ;;
  *)
    echo "Usage: scripts/dev.sh {start|stop|restart|preview|status}"
    exit 1
    ;;
esac
