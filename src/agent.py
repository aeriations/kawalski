from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import FunctionTool

import tools
import config

import asyncio

_agent = Agent(
    name=config.AGENT_NAME,
    model=LiteLlm(f"ollama_chat/{config.MODEL_NAME}"),
    instruction=config.SYSTEM_PROMPT,
    tools=tools.ALL_TOOLS,
)

_session = InMemorySessionService()
_runner = Runner(
    agent=_agent,
    app_name=config.AGENT_NAME,
    session_service=_session,
)

SESSION_ID = "main"
USER_ID = "user"

asyncio.get_event_loop().run_until_complete(
    _session.create_session(
        app_name=config.AGENT_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )
)

