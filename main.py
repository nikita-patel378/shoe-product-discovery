"""Shoe Product Discovery - RAG Chatbot for Running Shoe Specs."""

import chainlit as cl
from langchain_core.messages import AIMessage, HumanMessage

from agent import ShoeDiscoveryAgent


@cl.on_chat_start
async def start():
    """Initialize agent and send welcome message."""
    agent = ShoeDiscoveryAgent()
    cl.user_session.set("agent", agent)
    cl.user_session.set("chat_history", [])

    await cl.Message(
        content="""# 👟 Running Shoe Specs Finder

Ask me about **any running shoes** and I'll find their specs:
- Heel-to-toe drop
- Stack height
- Cushioning type
- Weight

**Examples:**
- "Tell me about the Nike Pegasus 41"
- "Compare ASICS Gel-Nimbus 26 and Brooks Ghost 16"
- "What's the stack height of the Hoka Clifton 9?"
- "Which has more cushioning: New Balance 1080v14 or Saucony Triumph 22?"

I use real-time web search to find the most accurate specifications."""
    ).send()


@cl.on_message
async def handle_message(message: cl.Message):
    """Handle incoming user messages with the LangChain agent."""
    agent: ShoeDiscoveryAgent = cl.user_session.get("agent")
    chat_history: list = cl.user_session.get("chat_history")

    user_input = message.content.strip()

    if not user_input:
        await cl.Message(content="Please ask about a running shoe!").send()
        return

    msg = cl.Message(content="")
    await msg.send()

    try:
        full_response = ""
        async for chunk in agent.stream(user_input, chat_history):
            full_response += chunk
            await msg.stream_token(chunk)

        await msg.update()

        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=full_response))

        if len(chat_history) > 20:
            chat_history = chat_history[-20:]

        cl.user_session.set("chat_history", chat_history)

    except Exception as e:
        msg.content = f"Error: {e}\n\nPlease try again or rephrase your question."
        await msg.update()
