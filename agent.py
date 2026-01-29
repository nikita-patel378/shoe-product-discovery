"""LangChain agent for shoe product discovery."""

import json
import os
from typing import AsyncIterator

from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from tools import AsyncShoeSearchTool, ShoeSearchTool, get_shoe_tools


def get_openai_api_key() -> str:
    """Get and validate the OpenAI API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is required. "
            "Get your key at https://platform.openai.com/api-keys"
        )
    return api_key

SYSTEM_PROMPT = """You are a running shoe expert assistant. Your job is to help users find
and compare running shoe specifications.

When users ask about shoes, use the available tools to search for accurate specifications:
- Use `shoe_specs_search` for a single shoe lookup
- Use `multi_shoe_search` when comparing 2+ shoes (more efficient)

Key specs to focus on:
- Heel-to-toe drop (mm): The height difference between heel and forefoot
- Stack height (mm): Total cushioning thickness under the heel/forefoot
- Cushioning: Type and level (plush, firm, responsive, etc.)
- Weight: In ounces or grams

When presenting results:
1. Start with a brief overview of each shoe
2. Present key specs clearly (use a table for comparisons)
3. Highlight notable differences when comparing
4. Cite your sources

If a shoe isn't found, suggest similar alternatives or ask for clarification."""


class ShoeDiscoveryAgent:
    """Agent for shoe product discovery using LangChain and Tavily."""

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.1,
    ) -> None:
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=get_openai_api_key(),
        )
        self.tools = get_shoe_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool by name."""
        for tool in self.tools:
            if tool.name == tool_name:
                if hasattr(tool, "_arun"):
                    if isinstance(tool_input, dict):
                        input_val = tool_input.get(
                            "shoe_names", tool_input.get("shoe_name", "")
                        )
                    else:
                        input_val = str(tool_input)
                    return await tool._arun(input_val)
                else:
                    if isinstance(tool_input, dict):
                        input_val = tool_input.get(
                            "shoe_name", tool_input.get("shoe_names", "")
                        )
                    else:
                        input_val = str(tool_input)
                    return tool._run(input_val)
        raise ValueError(f"Tool {tool_name} not found")

    async def run(
        self,
        user_input: str,
        chat_history: list | None = None,
    ) -> str:
        """Run the agent with user input and return the final response."""
        if chat_history is None:
            chat_history = []

        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        messages.extend(chat_history)
        messages.append(HumanMessage(content=user_input))

        while True:
            response = await self.llm_with_tools.ainvoke(messages)

            if not response.tool_calls:
                return response.content

            messages.append(response)

            for tool_call in response.tool_calls:
                tool_result = await self._execute_tool(
                    tool_call["name"],
                    tool_call["args"],
                )

                messages.append({
                    "role": "tool",
                    "content": tool_result,
                    "tool_call_id": tool_call["id"],
                })

    async def stream(
        self,
        user_input: str,
        chat_history: list | None = None,
    ) -> AsyncIterator[str]:
        """Stream the agent response for real-time output."""
        if chat_history is None:
            chat_history = []

        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        messages.extend(chat_history)
        messages.append(HumanMessage(content=user_input))

        while True:
            full_response = None

            async for chunk in self.llm_with_tools.astream(messages):
                if chunk.content:
                    yield chunk.content

                if full_response is None:
                    full_response = chunk
                else:
                    full_response = full_response + chunk

            # Tool calls are only complete on the accumulated message, not individual chunks
            if not full_response or not full_response.tool_calls:
                break

            messages.append(full_response)

            for tool_call in full_response.tool_calls:
                yield f"\n\n🔍 Searching for shoe specs...\n\n"

                tool_result = await self._execute_tool(
                    tool_call["name"],
                    tool_call["args"],
                )

                messages.append({
                    "role": "tool",
                    "content": tool_result,
                    "tool_call_id": tool_call["id"],
                })


async def quick_search(shoe_names: list[str]) -> dict:
    """Quick search without full agent - useful for simple lookups."""
    tool = AsyncShoeSearchTool()
    result = await tool._arun(", ".join(shoe_names))
    return json.loads(result)
