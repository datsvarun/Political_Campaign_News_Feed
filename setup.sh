#!/bin/bash

# Setup script for RSS Feed Scraper

echo "========================================="
echo "RSS Feed Scraper Setup"
echo "========================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Install dependencies
echo ""
echo "Installing dependencies..."

# Check for pip availability
if command -v pip3 &> /dev/null; then
    PIP_CMD=pip3
elif command -v pip &> /dev/null; then
    PIP_CMD=pip
else
    echo "✗ pip not found. Please install pip first."
    exit 1
fi

$PIP_CMD install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

# Check if config.py exists
if [ ! -f "config.py" ]; then
    echo ""
    echo "ℹ config.py not found. Using config.example.py as template."
    cp config.example.py config.py
    echo "✓ Created config.py from example"
    echo ""
    echo "⚠ Please edit config.py to customize your keywords and RSS feeds"
fi

# Check for credentials
echo ""
if [ ! -f "credentials.json" ]; then
    echo "⚠ credentials.json not found"
    echo ""
    echo "To use Google Docs integration, you need to:"
    echo "1. Go to https://console.cloud.google.com/"
    echo "2. Create a project and enable Google Docs API"
    echo "3. Create OAuth credentials (Desktop app)"
    echo "4. Download and save as credentials.json"
    echo ""
    echo "See README.md for detailed instructions."
else
    echo "✓ credentials.json found"
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit config.py to customize keywords and RSS feeds"
echo "2. Set up Google Docs credentials (see README.md)"
echo "3. Test the scraper: python test_scraper.py"
echo "4. Run the scraper: python main.py --mode once"
echo ""
