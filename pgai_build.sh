#!/bin/bash

set -e  # Exit on errors
set -u  # Treat unset variables as errors

# Define project directory and virtual environment path
PROJECT_DIR=$(pwd)
VENV_DIR="$PROJECT_DIR/venv"

# Helper function for logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log "Starting pgai CLI installation..."

# Step 1: Check and create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    log "Creating a virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    log "Virtual environment already exists at $VENV_DIR."
fi

# Step 2: Activate the virtual environment
log "Activating the virtual environment..."
source "$VENV_DIR/bin/activate"

# Step 3: Upgrade pip, setuptools, and wheel
log "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Step 4: Install the CLI as an editable package
log "Installing the pgai CLI tool..."
pip install --editable .

# Step 5: Add CLI activation to user's shell profile
log "Configuring the environment to activate CLI automatically..."
SHELL_PROFILE="$HOME/.bashrc"  # Default for bash
if [ "$SHELL" = "/bin/zsh" ]; then
    SHELL_PROFILE="$HOME/.zshrc"
fi

# Add venv activation and PATH setup if not already present
if ! grep -q "$VENV_DIR/bin" "$SHELL_PROFILE"; then
    echo -e "\n# Activate pgai CLI virtual environment" >> "$SHELL_PROFILE"
    echo "source $VENV_DIR/bin/activate" >> "$SHELL_PROFILE"
    log "Added virtual environment activation to $SHELL_PROFILE."
else
    log "Virtual environment activation already present in $SHELL_PROFILE."
fi

if ! grep -q "export PATH" "$SHELL_PROFILE"; then
    echo -e "\n# Add pgai CLI to PATH" >> "$SHELL_PROFILE"
    echo "export PATH=$PROJECT_DIR:\$PATH" >> "$SHELL_PROFILE"
    log "Added CLI to PATH in $SHELL_PROFILE."
else
    log "CLI path already present in $SHELL_PROFILE."
fi

# Reload shell profile
log "Reloading shell profile..."
source "$SHELL_PROFILE"

# Step 6: Verify CLI installation
log "Verifying the CLI installation..."
if command -v pgai &> /dev/null; then
    log "pgai CLI installed successfully! Test it with 'pgai --help'."
else
    log "Error: pgai command not found. Check the setup and try again."
    exit 1
fi

log "pgai CLI setup completed successfully!"
