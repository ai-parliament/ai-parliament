#!/bin/bash
# filepath: [setup.sh](http://_vscodecontentref_/2)

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: 'uv' is not installed. Install it with 'pip install uv' and try again."
    exit 1
fi

# Function to create a virtual environment
create_venv() {
    local dir=$1
    echo "Creating virtual environment in $dir..."
    cd $dir || exit
    uv venv .venv
    cd - || exit
}

# Create virtual environments for each subproject
create_venv "ai"
create_venv "backend"
create_venv "frontend"

echo "Virtual environments created successfully!"
