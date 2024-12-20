#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status
set -u  # Treat unset variables as an error and exit immediately

# Function to print messages with timestamps
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

log "Starting cleanup process..."

# Clean up Python build artifacts
log "Removing Python cache and build artifacts..."
find . -type d -name "__pycache__" -exec rm -rf {} +
rm -rf build dist *.egg-info UNKNOWN.egg-info

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    log "Virtual environment not found. Please create one using 'python3 -m venv venv' and re-run the script."
    exit 1
fi

# Activate virtual environment
log "Activating virtual environment..."
source venv/bin/activate

# Check if pip is installed
if ! command_exists pip; then
    log "pip is not installed in the virtual environment. Please install it and re-run the script."
    deactivate
    exit 1
fi

# Upgrade pip, setuptools, and wheel
log "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Rebuild the CLI
log "Rebuilding the CLI..."
pip install --editable .

# Verify the CLI installation
log "Verifying the CLI installation..."
if ! command_exists pgai; then
    log "CLI 'pgai' is not available. Ensure your setup.cfg or pyproject.toml defines the entry point correctly."
    deactivate
    exit 1
fi

log "Cleanup and rebuild completed successfully! Test the CLI with 'pgai --help'"

# Deactivate virtual environment
deactivate
