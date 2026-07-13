# Runtime Integrity Guard (RIG)

RIG is a high-performance, intelligent proxy middleware designed to secure Model Context Protocol (MCP) traffic. It acts as a transparent man-in-the-middle between an LLM client (e.g., Claude Desktop) and any MCP Server, actively inspecting JSON-RPC traffic to mitigate **tool-poisoning**, **rug-pulls**, and **prompt injection** attacks in real-time.

## Architecture

RIG is decoupled into two primary components for production reliability:

1. **The Data Plane (Python Proxy)**: A robust, multi-threaded interception proxy (`proxy.py`) that bridges `stdin/stdout` pipes. It passes payloads to the `RigEngine` for deep semantic inspection (using Gemini/Claude) and safely logs audit trails.
2. **The Control Plane (Next.js Dashboard)**: A modern, real-time React web application that streams intercepted events from the audit log, providing a sleek, GitHub Dark Mode-inspired interface for security monitoring.

## Directory Structure

```text
/
├── proxy.py              # Main entrypoint for the RIG Proxy
├── rig.py                # Core detection engine (Baseline, Heuristics, LLM Judge)
├── pre_cache.py          # Utility for building tool baseline hashes
├── rig_baseline.json     # Generated baseline hashes for known-safe tools
├── frontend/             # Next.js Application (Control Plane Dashboard)
├── tests/                # Test suites, mock servers, and malicious endpoints
├── legacy/               # Deprecated python reporting tools
└── docker-compose.yml    # Docker deployment configuration for the frontend
```

## Quick Start

### 1. Set Up the Proxy Engine

Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

Generate the security baseline for your server:
```bash
python pre_cache.py python tests/echo_server.py
```

### 2. Start the Control Center (Next.js)

The Next.js dashboard visualizes the traffic in real-time.

**Via Node.js:**
```bash
cd frontend
npm install
npm run dev
```

**Via Docker (Recommended for Production):**
```bash
docker-compose up -d --build
```
Access the dashboard at `http://localhost:3000`.

### 3. Attach RIG to Claude Desktop

To protect Claude Desktop, modify your `claude_desktop_config.json` to route traffic through the RIG proxy:

```json
{
  "mcpServers": {
    "protected-echo-server": {
      "command": "python",
      "args": [
        "C:\\absolute\\path\\to\\proxy.py",
        "python",
        "C:\\absolute\\path\\to\\tests\\echo_server.py"
      ]
    }
  }
}
```

## Security Pipeline

RIG employs a 4-layer defense-in-depth pipeline:
1. **Tool Integrity Verification:** Compares tools returned by the server against pre-computed SHA-256 baseline hashes.
2. **Context Window Protection:** Drops excessive payload sizes (e.g., >50,000 chars) designed to overwhelm the LLM.
3. **Pattern Matching:** Blocks known malicious regex signatures (e.g., `<system>`, `[PROMPT OVERRIDE]`).
4. **LLM Semantic Judge:** Uses a secondary LLM model (Gemini 2.5 Flash) to analyze the semantic intent of the payload, preventing sophisticated zero-day injections.
