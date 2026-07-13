import asyncio
import sys
from mcp.client.stdio import stdio_client
from mcp.client.stdio import StdioServerParameters
from mcp.client.session import ClientSession

async def main():
    print("--- Testing RIG with Malicious Server ---")
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["proxy.py", sys.executable, "malicious_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List tools
            tools = await session.list_tools()
            print("Tools available to agent:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # Call clean_tool (which has output injection)
            print("\nCalling clean_tool...")
            try:
                result = await session.call_tool("clean_tool", {})
                print(f"Tool result: {result}")
            except Exception as e:
                print(f"Error calling tool: {e}")

if __name__ == "__main__":
    asyncio.run(main())
