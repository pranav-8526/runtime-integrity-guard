<div align="center">

# 🛡️ Runtime Integrity Guard (RIG)

**An intelligent MCP proxy that detects and blocks tool-poisoning, rug-pull, and prompt injection attacks in real-time.**

[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js&logoColor=white)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-LLM_Judge-8E75B2?logo=google&logoColor=white)](https://ai.google.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## The Problem

The **Model Context Protocol (MCP)** lets LLMs call external tools — but those tool servers can be compromised. Attackers can:
- **Tool Poisoning:** Inject hidden instructions into tool descriptions to hijack LLM behavior.
- **Rug-Pull Attacks:** Swap safe tool definitions for malicious ones mid-session.
- **Prompt Injection:** Embed `<SYSTEM>` overrides or exfiltration commands in tool responses.

**RIG sits between the LLM client and the MCP server**, inspecting every JSON-RPC message in real-time to catch these attacks before they reach the model.

---

## Architecture

```mermaid
graph LR
    subgraph Client
        A["Claude Desktop / LLM Client"]
    end

    subgraph RIG["RIG Proxy - Data Plane"]
        B["proxy.py — stdin/stdout Bridge"]
        C["rig.py — 4-Layer Detection Engine"]
    end

    subgraph MCP["MCP Server"]
        D["Target Tool Server"]
    end

    subgraph Control["Control Plane"]
        E["Next.js Dashboard — Real-time Audit UI"]
        F["audit.jsonl — Structured Event Log"]
    end

    A -- "JSON-RPC" --> B
    B -- "Inspect" --> C
    C -- "ALLOW" --> B
    C -- "BLOCK" --> B
    B -- "Forward / Drop" --> D
    D -- "Response" --> B
    B -- "Log Event" --> F
    F -- "Stream" --> E

    style A fill:#1a1a2e,stroke:#58a6ff,color:#e6edf3
    style B fill:#161b22,stroke:#f85149,color:#e6edf3
    style C fill:#161b22,stroke:#f85149,color:#e6edf3
    style D fill:#1a1a2e,stroke:#3fb950,color:#e6edf3
    style E fill:#161b22,stroke:#58a6ff,color:#e6edf3
    style F fill:#0d1117,stroke:#8b949e,color:#8b949e
```

### Detection Pipeline (Defense in Depth)

| Layer | Name | Technique | Latency |
|:---:|---|---|:---:|
| **L1** | Baseline Integrity | SHA-256 hash comparison of tool schemas against a known-good snapshot | < 1ms |
| **L2** | Context Window Guard | Drops payloads exceeding safe token limits (>50k chars) to prevent context flooding | < 1ms |
| **L3** | Pattern Matching | Regex-based detection of known attack signatures (`<SYSTEM>`, `[PROMPT OVERRIDE]`, credential exfil patterns) | < 5ms |
| **L4** | LLM Semantic Judge | Sends suspicious payloads to Gemini 2.5 Flash for deep semantic analysis of intent | ~500ms |

---

## Directory Structure

```
├── proxy.py               # Data Plane: Multi-threaded stdin/stdout MCP proxy
├── rig.py                 # Core: 4-layer detection engine (L1-L4)
├── pre_cache.py           # Utility: Generates baseline hashes for tool schemas
├── requirements.txt       # Python dependencies
│
├── src/                   # Control Plane: Next.js Dashboard (App Router)
│   └── app/
│       ├── page.tsx       # Main dashboard UI (React + Tailwind)
│       ├── layout.tsx     # Root layout with metadata
│       ├── globals.css    # Design system tokens
│       └── api/logs/
│           └── route.ts   # Server API route (reads audit.jsonl)
│
├── tests/                 # Test infrastructure
│   ├── echo_server.py     # Benign MCP server for baseline testing
│   ├── malicious_server.py# Hostile MCP server with injection payloads
│   ├── test_rig_direct.py # Direct engine unit tests
│   └── run_all_tests.py   # Full E2E test harness
│
├── Dockerfile             # Multi-stage production container
├── docker-compose.yml     # One-command deployment
├── package.json           # Node.js dependencies
├── next.config.ts         # Next.js configuration (standalone output)
└── tsconfig.json          # TypeScript configuration
```

---

## Quick Start

### Prerequisites
- **Python 3.11+** with pip
- **Node.js 20+** with npm
- **Gemini API Key** (optional, for L4 LLM Judge)

### 1. Install Dependencies

```bash
# Python proxy engine
pip install -r requirements.txt

# Next.js dashboard
npm install
```

### 2. Generate Security Baseline

```bash
python pre_cache.py python tests/echo_server.py
```

### 3. Launch the Command Center

```bash
npm run dev
```

Open **http://localhost:3000** to access the real-time security dashboard.

### 4. Attach RIG to Claude Desktop

Edit your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "protected-server": {
      "command": "python",
      "args": [
        "C:/path/to/proxy.py",
        "python",
        "C:/path/to/tests/echo_server.py"
      ]
    }
  }
}
```

### 5. Run Attack Simulations

```bash
cd tests
python run_all_tests.py
```

---

## Docker Deployment

```bash
docker-compose up -d --build
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | — | API key for Gemini 2.5 Flash (enables L4 LLM Judge) |
| `RIG_LAYER4_SAMPLE_RATE` | `1.0` | Fraction of requests sent to L4 (0.0–1.0) |
| `RIG_LAYER4_CONFIDENCE_THRESHOLD` | `70.0` | Minimum confidence score to trigger a BLOCK verdict |
| `AUDIT_LOG_PATH` | `./audit.jsonl` | Override path for the structured audit log |

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Proxy Engine** | Python 3.11+, `subprocess`, `threading` | Multi-threaded stdin/stdout MCP bridge |
| **Detection Engine** | SHA-256, Regex, Google Gemini 2.5 Flash | 4-layer defense-in-depth pipeline |
| **Dashboard** | Next.js 16, React 19, TypeScript 5 | Real-time security monitoring UI |
| **Styling** | Tailwind CSS 4, Lucide Icons | GitHub Dark Mode-inspired design system |
| **Containerization** | Docker, Docker Compose | Production deployment |
| **Protocol** | JSON-RPC 2.0 (MCP Specification) | LLM ↔ Tool communication standard |
