import os
import sys
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
    StdioServerParameters,
)

load_dotenv()

# Absolute path to MCP server
current_dir = os.path.dirname(os.path.abspath(__file__))
mcp_server_path = os.path.join(current_dir, "mcp_server.py")

# MCP Toolset
toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[mcp_server_path],
            env=os.environ.copy(),
        ),
        timeout=60.0,
    )
)

# ADK Agent
github_card_agent = Agent(
    name="github_card_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are a GitHub profile analyst and dev card generator. "
        "When a user gives you a GitHub username, follow this sequence: "
        "1. Call scrape_github(username=username). "
        "2. Take the EXACT dictionary returned in 'structuredContent.result' "
        "   and pass it as 'github_data' to analyze_profile. "
        "3. Pass the 'github_data' AND the analysis result to generate_card_html. "
        "4. Finally, call save_card with the HTML. "
        "Never skip steps. Be enthusiastic!"
    ),
    tools=[toolset],
)