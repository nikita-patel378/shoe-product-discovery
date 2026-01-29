"""Pydantic models for shoe product discovery."""

from pydantic import BaseModel, Field


class ShoeSource(BaseModel):
    """A source URL with extracted content."""

    title: str
    url: str
    content: str
    score: float = Field(default=0.0, description="Relevance score 0-1")


class ShoeSpecs(BaseModel):
    """Specifications for a running shoe."""

    name: str = Field(description="Full shoe name (brand + model)")
    heel_to_toe_drop: str | None = Field(default=None, description="Drop in mm")
    stack_height: str | None = Field(default=None, description="Stack height in mm")
    cushioning: str | None = Field(default=None, description="Cushioning type/level")
    weight: str | None = Field(default=None, description="Weight in oz/g")
    summary: str = Field(description="Brief overview of the shoe")
    sources: list[ShoeSource] = Field(default_factory=list)


class ShoeSearchResult(BaseModel):
    """Result from a shoe search query."""

    query: str
    shoes: list[ShoeSpecs] = Field(default_factory=list)
    raw_answer: str | None = Field(default=None, description="Raw Tavily answer")


class ShoeComparisonRequest(BaseModel):
    """Request to compare multiple shoes."""

    shoe_names: list[str] = Field(min_length=1, max_length=5)
    focus_attributes: list[str] = Field(
        default_factory=lambda: ["heel_to_toe_drop", "stack_height", "cushioning"]
    )
