import asyncio

from google.adk.runners import InMemoryRunner
from google.genai import types

from app.agent import app


async def run_test():
    runner = InMemoryRunner(app=app)
    session = await runner.session_service.create_session(
        app_name="app", user_id="test_user"
    )
    async for event in runner.run_async(
        user_id="test_user",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part.from_text(text="start")]),
    ):
        print(f"Event type: {type(event)}, Output: {event.output}")

if __name__ == "__main__":
    asyncio.run(run_test())
