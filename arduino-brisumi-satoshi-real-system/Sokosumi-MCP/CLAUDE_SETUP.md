# 🤖 Claude Desktop Integration (Optional - Testing Only)

> **Note:** This integration is for hackathon testing purposes only and is NOT part of the main Arduino plant monitoring pipeline.

## Overview

The Sokosumi MCP server can be integrated with Claude Desktop for manual testing and interaction with Sokosumi AI agents.

## Prerequisites

- Claude Desktop installed
- Sokosumi API key (from `.env` file)
- Python 3.11+ with MCP dependencies

## Quick Setup

### Option 1: Use Sokosumi's Hosted MCP (Recommended)

1. **Use the MCP URL from `.env`:**
   ```
   https://mcp.sokosumi.com/mcp?api_key=YOUR_API_KEY&network=mainnet
   ```

2. **Add to Claude Desktop:**
   - Open Claude Desktop
   - Go to **Settings** → **Developer** → **Edit Config**
   - Add the MCP server configuration:

   ```json
   {
     "mcpServers": {
       "sokosumi": {
         "command": "python",
         "args": ["-m", "mcp", "run", "sse", "https://mcp.sokosumi.com/mcp?api_key=YOUR_API_KEY&network=mainnet"]
       }
     }
   }
   ```

3. **Restart Claude Desktop**

### Option 2: Run Local MCP Server

1. **Install dependencies:**
   ```powershell
   cd Sokosumi-MCP
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```powershell
   python server.py
   ```

3. **Add to Claude Desktop config:**
   ```json
   {
     "mcpServers": {
       "sokosumi-local": {
         "command": "python",
         "args": ["C:/path/to/Sokosumi-MCP/server.py"],
         "env": {
           "SOKOSUMI_API_KEY": "your_api_key_here",
           "SOKOSUMI_NETWORK": "mainnet"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop**

## Available MCP Tools

Once connected, Claude Desktop will have access to:

- `list_agents` - List available AI agents
- `get_user_profile` - Get your Sokosumi profile
- `create_job` - Create analysis jobs
- `get_job` - Check job status
- `wait_for_job` - Wait for job completion

## Example Usage in Claude

```
Claude, using Sokosumi:
- List all available AI agents
- Create a plant health analysis job for my Aloe Vera
- Check the status of job #12345
```

## Testing

Use the included test client:

```powershell
cd Sokosumi-MCP
python test_client.py
```

## Important Notes

⚠️ **This integration is for testing only:**
- Not used in the main Arduino → Bridge → Report pipeline
- Response times are ~5 minutes (too slow for real-time hardware)
- Requires manual interaction through Claude Desktop
- Main system uses local analysis for instant results

✅ **Main pipeline uses:**
- Local rule-based analysis (< 1ms)
- Instant report generation
- No external API dependencies
- Perfect for IoT/embedded systems

## Troubleshooting

### "Module 'mcp' not found"
```powershell
pip install mcp>=1.2.0
```

### "Connection refused"
- Check that `server.py` is running
- Verify API key in `.env` file
- Check Python path in Claude config

### "Job timeout"
- Sokosumi jobs can take 5+ minutes
- Use `wait_for_job` tool with patience
- Check job status manually in Sokosumi dashboard

## Architecture

```
┌──────────────────┐
│ Claude Desktop   │  ← Manual testing interface
│  (MCP Client)    │
└────────┬─────────┘
         │ STDIO
         ▼
┌──────────────────┐
│ Sokosumi MCP     │  ← Optional testing server
│   server.py      │
└────────┬─────────┘
         │ API
         ▼
┌──────────────────┐
│ Sokosumi Cloud   │
│   AI Agents      │
└──────────────────┘

                   ❌ NOT connected to main pipeline ❌

┌──────────────────┐
│ Arduino Sensors  │  ← Production pipeline
└────────┬─────────┘
         │ Serial
         ▼
┌──────────────────┐
│ Arduino Bridge   │  ← Uses local analysis
│   Node.js        │
└────────┬─────────┘
         │ Instant
         ▼
┌──────────────────┐
│ Plant Reports    │  ← Fast, reliable, offline
└──────────────────┘
```

## Resources

- [Sokosumi Dashboard](https://app.sokosumi.com)
- [Sokosumi MCP Documentation](https://sokosumi.com/docs/mcp)
- [Claude Desktop MCP Guide](https://docs.anthropic.com/claude/docs/model-context-protocol)

---

**For hackathon team:** Feel free to test Sokosumi MCP through Claude Desktop, but remember the main system uses local analysis for production reliability.
