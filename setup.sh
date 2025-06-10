#!/bin/bash
# Setup script for StoreHub MCP Server

set -e

echo "🚀 Setting up StoreHub MCP Server..."

# Create virtual environment
cd storehub-mcp-server
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file template
if [ ! -f .env ]; then
    cp .env.template .env
    echo "📄 Created .env file from template"
fi

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit storehub-mcp-server/.env and add your StoreHub API credentials"
echo "2. Test the server: cd storehub-mcp-server && source venv/bin/activate && python main.py"
echo "3. Configure Claude to use this MCP server"
echo ""
echo "⚠️  Note: The server will run with mock data until you configure real API credentials" 