import asyncio
import sys
from mcp.client.stdio import stdio_client
from mcp.client.stdio import StdioServerParameters
from mcp.client.session import ClientSession

async def main():
    # Run the proxy, which runs the echo_server
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["proxy.py", sys.executable, "echo_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List tools
            tools = await session.list_tools()
            print("Tools available:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # Call tool
            result = await session.call_tool("echo", {"message": "Hello from mock client!"})
            print(f"Tool result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
