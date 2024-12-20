#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.
set -u  # Treat unset variables as errors.

# Helper function for logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

DATABASE="postgres"
PORT="5432"
USER="postgres"
PG_BIN="/usr/local/pg16/bin"
DATA_DIR="/usr/local/pg16/data"

# Clean any existing PostgreSQL process on port 5432
log "Checking and cleaning any PostgreSQL process running on port $PORT..."
if lsof -i :$PORT | grep LISTEN > /dev/null 2>&1; then
    lsof -i :$PORT | awk '{print $2}' | xargs sudo kill -9 || true
    log "Cleared processes using port $PORT."
else
    log "No processes using port $PORT."
fi

# Run the pgai commands in order
log "Running 'pgai install'..."
pgai install pg16 --force-init --clean

log "Starting PostgreSQL server temporarily..."
"$PG_BIN/pg_ctl" start -D "$DATA_DIR" -l "$DATA_DIR/logfile" -w

log "Ensuring the 'postgres' superuser role exists..."
"$PG_BIN/psql" -p "$PORT" -d "$DATABASE" -c "DO \$\$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'postgres') THEN
        CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'postgres';
    END IF;
END \$\$;"

log "Stopping PostgreSQL server..."
"$PG_BIN/pg_ctl" stop -D "$DATA_DIR" -m immediate

log "Running 'pgai start'..."
pgai start

log "Running 'pgai status'..."
pgai status

log "Running 'pgai run' to connect to psql..."
pgai run "$DATABASE" --p "$PORT" -u postgres

# Once psql is exited, we reach here
log "Exited psql session."
