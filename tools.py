"""LangChain tools for shoe product discovery."""

import asyncio
import os
from typing import Any

from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, Field
from tavily import AsyncTavilyClient, TavilyClient

from models import ShoeSearchResult, ShoeSource, ShoeSpecs


def get_tavily_api_key() -> str:
    """Get and validate the Tavily API key from environment."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError(
            "TAVILY_API_KEY environment variable is required. "
            "Get your key at https://tavily.com"
        )
    return api_key


# Trusted domains for shoe specifications
SHOE_DOMAINS = [
    "runrepeat.com",
    "solereview.com",
    "believeintherun.com",
    "roadrunnersports.com",
    "runnersworld.com",
    "doctorsofrunning.com",
    
]


class ShoeSearchInput(BaseModel):
    """Input schema for shoe search tool."""

    shoe_name: str = Field(description="Name of the running shoe to search for")


class ShoeSearchTool(BaseTool):
    """Tool for searching running shoe specifications using Tavily."""

    name: str = "shoe_specs_search"
    description: str = (
        "Search for running shoe specifications including heel-to-toe drop, "
        "stack height, cushioning, and weight. Input should be a shoe name "
        "like 'Nike Pegasus 41' or 'ASICS Gel-Nimbus 26'."
    )
    args_schema: type[BaseModel] = ShoeSearchInput
    return_direct: bool = False

    client: TavilyClient | None = None
    use_domain_filter: bool = True
    search_depth: str = "advanced"

    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if self.client is None:
            self.client = TavilyClient(api_key=get_tavily_api_key())

    def _build_query(self, shoe_name: str) -> str:
        """Build an optimized search query for shoe specs."""
        return f"{shoe_name} running shoe specs heel drop stack height weight"

    def _parse_response(self, shoe_name: str, response: dict) -> ShoeSpecs:
        """Parse Tavily response into structured ShoeSpecs."""
        sources = [
            ShoeSource(
                title=r.get("title", ""),
                url=r.get("url", ""),
                content=r.get("content", "")[:500],
                score=r.get("score", 0.0),
            )
            for r in response.get("results", [])
            if r.get("score", 0) > 0.5
        ]

        return ShoeSpecs(
            name=shoe_name,
            summary=response.get("answer", "No specifications found."),
            sources=sources[:3],
        )

    def _run(self, shoe_name: str) -> str:
        """Synchronous shoe search."""
        try:
            query = self._build_query(shoe_name)

            search_params = {
                "query": query,
                "search_depth": self.search_depth,
                "max_results": 5,
                "include_answer": "advanced",
            }

            if self.use_domain_filter:
                search_params["include_domains"] = SHOE_DOMAINS

            response = self.client.search(**search_params)
            specs = self._parse_response(shoe_name, response)

            return specs.model_dump_json(indent=2)

        except Exception as e:
            raise ToolException(f"Failed to search for {shoe_name}: {e}") from e


class AsyncShoeSearchTool(BaseTool):
    """Async tool for searching multiple shoes in parallel."""

    name: str = "multi_shoe_search"
    description: str = (
        "Search for specifications of multiple running shoes in parallel. "
        "Input should be comma-separated shoe names like "
        "'Nike Pegasus 41, ASICS Gel-Nimbus 26, Brooks Ghost 16'. "
        "Use this when comparing multiple shoes."
    )
    return_direct: bool = False

    async_client: AsyncTavilyClient | None = None
    use_domain_filter: bool = True
    search_depth: str = "advanced"
    max_shoes: int = 5

    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if self.async_client is None:
            self.async_client = AsyncTavilyClient(api_key=get_tavily_api_key())

    def _build_query(self, shoe_name: str) -> str:
        """Build an optimized search query for shoe specs."""
        return f"{shoe_name} running shoe specs heel drop stack height weight"

    def _parse_response(self, shoe_name: str, response: dict) -> ShoeSpecs:
        """Parse Tavily response into structured ShoeSpecs."""
        sources = [
            ShoeSource(
                title=r.get("title", ""),
                url=r.get("url", ""),
                content=r.get("content", "")[:500],
                score=r.get("score", 0.0),
            )
            for r in response.get("results", [])
            if r.get("score", 0) > 0.5
        ]

        return ShoeSpecs(
            name=shoe_name,
            summary=response.get("answer", "No specifications found."),
            sources=sources[:3],
        )

    async def _search_single(self, shoe_name: str) -> ShoeSpecs:
        """Search for a single shoe asynchronously."""
        query = self._build_query(shoe_name)

        search_params = {
            "query": query,
            "search_depth": self.search_depth,
            "max_results": 5,
            "include_answer": "advanced",
        }

        if self.use_domain_filter:
            search_params["include_domains"] = SHOE_DOMAINS

        response = await self.async_client.search(**search_params)
        return self._parse_response(shoe_name, response)

    def _run(self, shoe_names: str) -> str:
        """Synchronous wrapper for async search."""
        return asyncio.run(self._arun(shoe_names))

    async def _arun(self, shoe_names: str) -> str:
        """Async multi-shoe search."""
        try:
            names = [n.strip() for n in shoe_names.split(",")]
            names = [n for n in names if n][:self.max_shoes]

            if not names:
                raise ToolException("No valid shoe names provided")

            results = await asyncio.gather(
                *[self._search_single(name) for name in names],
                return_exceptions=True,
            )

            shoes = []
            for name, result in zip(names, results):
                if isinstance(result, Exception):
                    shoes.append(
                        ShoeSpecs(name=name, summary=f"Search failed: {result}")
                    )
                else:
                    shoes.append(result)

            search_result = ShoeSearchResult(
                query=shoe_names,
                shoes=shoes,
            )

            return search_result.model_dump_json(indent=2)

        except Exception as e:
            raise ToolException(f"Multi-shoe search failed: {e}") from e


def get_shoe_tools() -> list[BaseTool]:
    """Get all shoe discovery tools."""
    return [
        ShoeSearchTool(),
        AsyncShoeSearchTool(),
    ]
