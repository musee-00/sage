# Sage — Local AI Code Assistant

Sage is a locally-running AI coding assistant that lives inside VS Code. It uses a local language model (via Ollama) to read files, write code, run terminal commands, and search your codebase — all without sending data to the cloud.

## Features

- **Agentic tool use** — the model autonomously decides when to read files, write code, run shell commands, or search for patterns
- **VS Code sidebar panel** — chat with Sage directly inside your editor
- **Web UI** — also accessible at `http://localhost:5001` in any browser
- **MCP server** — exposes the agent as a Model Context Protocol tool for other integrations
- **Fully local** — no API keys, no internet connection required

## Tech Stack

| Layer | Technology |
|---|---|
| LLM runtime | [Ollama](https://ollama.com) |
| Model | `qwen2.5:7b` |
| Backend | Python 3.12, Flask |
| VS Code integration | VS Code Extension API (Webview) |
| MCP server | `mcp` Python SDK |

## Requirements

- [Ollama](https://ollama.com) installed and running
- Python 3.10+
- `qwen2.5:7b` model pulled

## Installation

```bash
# 1. Pull the model
ollama pull qwen2.5:7b

# 2. Install Python dependencies
pip install flask flask-cors ollama mcp

# 3. Install the VS Code extension
cp -r vscode-extension ~/.vscode/extensions/sage.sage-assistant-0.0.1
```

## Running

```bash
python server.py
```

The server starts on `http://localhost:5001`. Open VS Code and the Sage panel will appear in the activity bar (🌿).

VS Code can also auto-start the server when the folder is opened — see `.vscode/tasks.json`.

## Agent Tools

The agent has access to five tools it can invoke autonomously:

| Tool | Description |
|---|---|
| `read_file` | Read any file on disk |
| `write_file` | Write content to a file |
| `run_command` | Execute a shell command |
| `search_code` | Search for patterns across source files (grep) |
| `list_files` | List files in a directory |

## Future Improvements

- Markdown rendering in the chat UI (code blocks, syntax highlighting)
- Streaming responses so output appears word-by-word
- Show which tools the agent is calling in real time
- Per-project context (automatically include relevant files in the prompt)
- Switch models without restarting the server
