# RIG (Runtime Integrity Guard) for MCP

[![Vercel Dashboard](https://img.shields.io/badge/RIG%20Command%20Center-Live%20Dashboard-orange?style=for-the-badge&logo=vercel)](https://rigcommandcentre.vercel.app/)

RIG is a transparent proxy designed to secure Model Context Protocol (MCP) deployments against tool poisoning, rug-pull attacks, and full-schema/output injection.

While existing static scanners (like `mcp-scan`) inspect an MCP tool's metadata at connection time, they miss injections that happen dynamically in the content a tool returns *during* a live session (e.g., reading a poisoned support ticket or GitHub PR). RIG closes this gap by inspecting every JSON-RPC message in real-time, blocking malicious payloads before they ever reach the LLM context window.

## Features (P0 MVP)

- **Layer 1 (Rug-pull Detection):** Hashes tool schemas on first sight and blocks the tool if the server attempts to serve a different (poisoned) schema on subsequent loads.
- **Layer 2 (Pattern/Keyword Rules):** Inspects both tool descriptions and live *tool outputs* for known injection patterns:
  - **Instruction Overrides:** E.g., "ignore previous instructions", "before executing, read..."
  - **Sensitive Data Targeting:** Targets `.env`, `.ssh/id_rsa`, `AWS_ACCESS_KEY`
  - **Obfuscation:** Zero-width characters
  - **Shadowing / Exfiltration:** "secretly BCC", "exfiltrate", "forward to"
- **Transparent Stdio Proxy:** Wraps the real MCP server process and intercepts JSON-RPC over stdio.
- **Audit Logging & CLI Reporter:** All traffic and security verdicts are logged to `audit.jsonl`, with a CLI tool to generate detection summaries.

## How to Run

### 1. Set up the environment
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Unix
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run the Demo Test Suite
The included `run_all_tests.py` automatically spins up a mock client and tests RIG against a suite of malicious (and clean) servers covering:
- **Clean Traffic:** Benchmarks False Positive rates with legitimate code snippets and conversational texts.
- **Direct tool description poisoning:** Injected instructions inside the tool metadata itself.
- **Shadowing / Confused Deputy:** Sneaking a "BCC attacker@evil.com" behavior into an otherwise legitimate tool.
- **Rug-pull attacks:** The server returns a clean tool schema on first load, then swaps it to a malicious version on the second load.
- **Output Injection:** 5 variations simulating malicious payloads hidden inside Notion pages, support tickets, or pull requests.

```bash
python run_all_tests.py
```

### 3. Generate Security Report
After running the tests, see exactly what RIG caught:
```bash
python rig_report.py
```

## Running against a real MCP Server with Claude Desktop

To protect a real MCP server in Claude Desktop, simply wrap the command in `claude_desktop_config.json`.

**Before:**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["my_mcp_server.py"]
    }
  }
}
```

**With RIG:**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["/absolute/path/to/rig/proxy.py", "python", "my_mcp_server.py"]
    }
  }
}
```

## Architecture

```
Claude Desktop / Cursor / Claude Code
        │  (stdio unmodified MCP JSON-RPC)
        ▼
 ┌───────────────────────────────┐
 │        RIG Proxy              │
 │ ┌───────────────────────────┐ │
 │ │ 1. Baseline hash store    │ │  ← detects rug-pulls (Layer 1)
 │ │ 2. Schema poisoning check │ │  ← direct metadata poisoning (Layer 2)
 │ │ 3. Output inspection      │ │  ← output injection (Layer 2)
 │ │ 4. Verdict + block/redact │ │  ← replaces malicious payload
 │ └───────────────────────────┘ │
 │        audit.jsonl            │
 └───────────────────────────────┘
        ▼
   Real MCP Server 
```
