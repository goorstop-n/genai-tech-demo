import random
from mcp.server.fastmcp import FastMCP


# Initialize FastMCP server
mcp = FastMCP("weather", log_level="ERROR")


# Constants
USER_AGENT = "weather-app/1.0"


@mcp.tool()
async def get_weather(location: str) -> dict:
    """
    Retrieves current weather for the given location.

    Args:
        location: city e.g. 北京，上海.
    """
    # mock weather results.
    results = [
        {"weather": "晴", "temperature": 20},
        {"weather": "多云", "temperature": 15},
        {"weather": "小雨", "temperature": 10}
    ]

    return results[random.randint(0, len(results) - 1)]


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
