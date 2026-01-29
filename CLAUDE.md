# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A running shoe product discovery chatbot using LangChain agents with Tavily search. The app helps users find and compare running shoe specifications (heel drop, stack height, cushioning, weight).

## Development Setup

This project uses Python 3.13 with a virtual environment managed via `.venv/`.

### Environment Variables

Required:
- `TAVILY_API_KEY` - Get from https://tavily.com
- `OPENAI_API_KEY` - For LangChain agent LLM

### Running the Application

```bash
# Chainlit web interface
chainlit run main.py

# CLI interactive mode
uv run python cli.py

# CLI quick search
uv run python cli.py "Nike Pegasus 41" "Brooks Ghost 16"
```

### Virtual Environment

The project uses a `.venv` directory. Activate it before development:

```bash
source .venv/bin/activate
```

## Architecture

```
├── main.py          # Chainlit web interface
├── cli.py           # CLI interface for testing/scripting
├── agent.py         # LangChain agent orchestration
├── tools.py         # LangChain tools (Tavily shoe search)
└── models.py        # Pydantic models for type safety
```

### Key Components

**Tools (`tools.py`):**
- `ShoeSearchTool` - Single shoe lookup
- `AsyncShoeSearchTool` - Parallel multi-shoe search

**Agent (`agent.py`):**
- `ShoeDiscoveryAgent` - Orchestrates tools with LLM reasoning
- `quick_search()` - Direct tool access without agent overhead

**Models (`models.py`):**
- `ShoeSpecs` - Structured shoe specification data
- `ShoeSearchResult` - Search result container

## Extending

To add new tools (e.g., price search, reviews):

1. Create tool class in `tools.py` inheriting from `BaseTool`
2. Add to `get_shoe_tools()` function
3. Update agent system prompt if needed
