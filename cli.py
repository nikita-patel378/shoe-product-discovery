"""CLI interface for shoe discovery - useful for testing and scripting."""

import asyncio
import sys

from agent import ShoeDiscoveryAgent, quick_search


async def interactive_mode():
    """Run interactive chat session."""
    print("🏃 Running Shoe Discovery CLI")
    print("Type 'quit' to exit\n")

    agent = ShoeDiscoveryAgent()
    chat_history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if not user_input:
            continue

        print("\nAssistant: ", end="", flush=True)

        async for chunk in agent.stream(user_input, chat_history):
            print(chunk, end="", flush=True)

        print("\n")


async def search_mode(shoe_names: list[str]):
    """Quick search for specific shoes."""
    print(f"Searching for: {', '.join(shoe_names)}\n")

    result = await quick_search(shoe_names)

    for shoe in result.get("shoes", []):
        print(f"{'='*50}")
        print(f"📦 {shoe['name'].upper()}")
        print(f"{'='*50}")
        print(f"\n{shoe['summary']}\n")

        if shoe.get("sources"):
            print("Sources:")
            for src in shoe["sources"]:
                print(f"  - {src['title']}")
                print(f"    {src['url']}")
        print()


def main():
    """Main CLI entry point."""
    if len(sys.argv) > 1:
        shoe_names = sys.argv[1:]
        asyncio.run(search_mode(shoe_names))
    else:
        asyncio.run(interactive_mode())


if __name__ == "__main__":
    main()
