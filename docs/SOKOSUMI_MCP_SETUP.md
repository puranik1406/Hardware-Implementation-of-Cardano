# Sokosumi MCP: Local Development Setup

This project can integrate with the official Sokosumi MCP server for development/testing. We do not duplicate their code—follow their repo and docs.

## Prerequisites
- Python 3.8+
- A Sokosumi account with API access

## Steps
1) Clone the official repo

```
git clone https://github.com/masumi-network/Sokosumi-MCP.git
cd Sokosumi-MCP
```

2) Create and activate a virtual environment

- Windows
```
python -m venv venv
venv\Scripts\activate
```
- macOS/Linux
```
python3 -m venv venv
source venv/bin/activate
```

3) Install dependencies
```
pip install -r requirements.txt
```

4) Configure environment
```
cp .env.example .env
# Edit .env
SOKOSUMI_API_KEY=your_api_key_here
SOKOSUMI_NETWORK=preprod   # or mainnet
```

5) Run the MCP server locally
```
python server.py
```

6) (Optional) Test with included client
```
python test_client.py
```

## Claude Desktop configuration
On Windows: %APPDATA%\Claude\claude_desktop_config.json

```
{
  "mcpServers": {
    "sokosumi": {
      "command": "python",
      "args": ["/absolute/path/to/Sokosumi-MCP/server.py"],
      "env": {
        "SOKOSUMI_API_KEY": "your-api-key-here",
        "SOKOSUMI_NETWORK": "preprod"
      }
    }
  }
}
```

Restart Claude Desktop to load the local MCP server.
