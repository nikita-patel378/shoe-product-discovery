# Running Shoe Product Discovery

A chatbot for discovering and comparing running shoe specifications, built as a practice project using **Claude Code** to vibe code an AI-powered application.

## Purpose

This project was created to explore rapid prototyping with Claude Code, combining:

- **Tavily Web Search** - Real-time web search API for fetching shoe specs from trusted running shoe domains
- **LangChain** - Agent orchestration and tool integration
- **Chainlit** - Interactive chat UI for the web interface

The app searches trusted sources like RunRepeat, SoleReview, Believe in the Run, and Runner's World to find accurate shoe specifications.

## Features

- Look up specs for any running shoe (heel drop, stack height, cushioning, weight)
- Compare multiple shoes side-by-side
- Real-time streaming responses
- Both web UI and CLI interfaces

## Quick Start

### Prerequisites

- Python 3.13+
- [Tavily API key](https://tavily.com)
- [OpenAI API key](https://platform.openai.com/api-keys)

### Setup

```bash
# Clone and enter directory
cd shoe-product-discovery

# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync

# Set environment variables
export TAVILY_API_KEY="your-tavily-key"
export OPENAI_API_KEY="your-openai-key"
```

### Run

```bash
# Web interface (Chainlit)
chainlit run main.py

# CLI interactive mode
uv run python cli.py

# CLI quick search
uv run python cli.py "Nike Pegasus 41" "Brooks Ghost 16"
```

## Architecture

```
├── main.py      # Chainlit web interface
├── cli.py       # CLI for testing/scripting
├── agent.py     # LangChain agent orchestration
├── tools.py     # Tavily search tools with domain filtering
└── models.py    # Pydantic models for type safety
```

### Trusted Domains

The search tools filter results to these running shoe authorities:

- runrepeat.com
- solereview.com
- believeintherun.com
- roadrunnersports.com
- runnersworld.com
- doctorsofrunning.com

## Example Queries

- "Tell me about the Nike Pegasus 41"
- "Compare ASICS Gel-Nimbus 26 and Brooks Ghost 16"
- "What's the stack height of the Hoka Clifton 9?"
- "Which has more cushioning: New Balance 1080v14 or Saucony Triumph 22?"

## Built With

- [Tavily](https://tavily.com) - AI-optimized web search
- [LangChain](https://langchain.com) - LLM application framework
- [Chainlit](https://chainlit.io) - Chat UI framework
- [Claude Code](https://claude.ai/code) - AI coding assistant used to build this project
