import asyncio
import os
import subprocess
import sys
import time
import httpx
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

load_dotenv()

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/sse")


# ─────────────────────────────────────────
# Start MCP Server as a subprocess
# ─────────────────────────────────────────
def start_mcp_server():
    print("🔌 Starting MCP Server...")
    process = subprocess.Popen(
        [sys.executable, "server.py"],
        cwd=os.path.join(os.path.dirname(__file__), "mcp_server"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return process


# ─────────────────────────────────────────
# Wait until MCP Server is ready
# ─────────────────────────────────────────
async def wait_for_mcp_server(retries: int = 10, delay: float = 2.0):
    print("⏳ Waiting for MCP Server to be ready...")
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    MCP_SERVER_URL.replace("/sse", "/"),
                    timeout=3.0
                )
                print("✅ MCP Server is ready!")
                return True
        except Exception:
            print(f"   Attempt {attempt + 1}/{retries} — not ready yet, retrying in {delay}s...")
            await asyncio.sleep(delay)
    print("❌ MCP Server did not start in time.")
    return False


# ─────────────────────────────────────────
# Run the multi-agent pipeline
# ─────────────────────────────────────────
async def run_pipeline(location: str):
    # Import root_agent here to avoid circular imports
    from coordinator_agent.agent import root_agent

    # Set up session service and runner
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="weather-retail-events-app",
        session_service=session_service
    )

    # Create a new session
    session = await session_service.create_session(
        app_name="weather-retail-events-app",
        user_id="user_01"
    )

    print(f"\n🚀 Running pipeline for location: {location}")
    print("─" * 60)

    # Create user message with location
    user_message = Content(
        role="user",
        parts=[Part(text=f"My location is {location}. Please give me the weather, clothing recommendation and any upcoming events near me.")]
    )

    # Run the agent pipeline
    async for event in runner.run_async(
        user_id="user_01",
        session_id=session.id,
        new_message=user_message
    ):
        # Print final response from coordinator
        if event.is_final_response():
            print("\n📋 FINAL RESPONSE:")
            print("─" * 60)
            print(event.content.parts[0].text)
            print("─" * 60)


# ─────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────
async def main():
    print("=" * 60)
    print("🤖 Multi-Agent System — Weather + Retail + Events")
    print("=" * 60)

    # Get location from user
    location = input("\n📍 Enter your location (e.g. 'New York', 'London'): ").strip()
    if not location:
        print("❌ No location provided. Exiting.")
        return

    # Start MCP server
    mcp_process = start_mcp_server()

    try:
        # Wait for MCP server to be ready
        server_ready = await wait_for_mcp_server()
        if not server_ready:
            mcp_process.terminate()
            return

        # Run the pipeline
        await run_pipeline(location)

    finally:
        # Shutdown MCP server
        print("\n🛑 Shutting down MCP Server...")
        mcp_process.terminate()
        mcp_process.wait()
        print("✅ MCP Server stopped. Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())