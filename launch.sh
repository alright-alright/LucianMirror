#!/bin/bash

# LucianMirror Launch Script (Unix/Linux/Mac)

echo "🚀 Starting LucianMirror..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Run the Python launcher
python3 launch.py