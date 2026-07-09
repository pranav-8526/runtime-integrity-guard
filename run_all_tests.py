import asyncio
import sys
import os
from mcp.client.stdio import stdio_client
from mcp.client.stdio import StdioServerParameters
from mcp.client.session import ClientSession

async def run_test(mode):
    print(f"\n--- Running Test Mode: {mode} ---")
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["proxy.py", sys.executable, os.path.join("test_servers", "suite.py"), "--mode", mode],
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                tools = await session.list_tools()
                
                if tools.tools:
                    tool_name = tools.tools[0].name
                    print(f"Calling tool: {tool_name}")
                    result = await session.call_tool(tool_name, {})
                    print(f"Result: {result.content[0].text if result.content else result}")
                else:
                    print("No tools returned (likely blocked by RIG Layer 1 or 2).")
    except Exception as e:
        print(f"Test {mode} ended with error (could be blocked connection): {e}")

async def main():
    if os.path.exists("audit.jsonl"):
        os.remove("audit.jsonl")
    if os.path.exists("rig_baseline.json"):
        os.remove("rig_baseline.json")
    if os.path.exists("rug_pull_state.txt"):
        os.remove("rug_pull_state.txt")

    modes = [
        "direct_poisoning",
        "shadowing",
        "rug_pull",           
        "rug_pull",           
        "output_injection_1",
        "output_injection_2",
        "output_injection_3",
        "output_injection_4",
        "output_injection_5",
        "clean_traffic_1",
        "clean_traffic_2",
    ]
    
    for mode in modes:
        await run_test(mode)
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())