import asyncio
import sys
import os
import json
from mcp.client.stdio import stdio_client
from mcp.client.stdio import StdioServerParameters
from mcp.client.session import ClientSession

async def run_test(mode_id, server_mode, expected_verdict, attack_class):
    print(f"\n--- Running Test Mode: {mode_id} ---")
    env = os.environ.copy()
    if mode_id == "layer4_rate_limit_mock":
        env["MOCK_RATE_LIMIT"] = "1"

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["proxy.py", sys.executable, os.path.join("test_servers", "suite.py"), "--mode", server_mode],
        env=env
    )

    actual_verdict = "ALLOW"
    error_msg = ""
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                tools = await session.list_tools()
                schema_blocked_modes = ["direct_poisoning", "shadowing", "rug_pull_2", "rug_pull_3", "rug_pull_4"]
                
                if not tools.tools:
                    actual_verdict = "BLOCK"
                    if expected_verdict == "BLOCK":
                        print(f"PASS: {mode_id} correctly blocked at schema level.")
                    else:
                        print(f"FAIL: {mode_id} falsely blocked at schema level!")
                else:
                    if mode_id in schema_blocked_modes:
                        actual_verdict = "ALLOW"
                        print(f"FAIL: {mode_id} expected schema block but was allowed!")
                    else:
                        tool_name = tools.tools[0].name
                        print(f"Calling tool: {tool_name}")
                        result = await session.call_tool(tool_name, {})
                        content_text = result.content[0].text if result.content else str(result)
                        print(f"Result: {content_text}")
                        
                        if "[RIG BLOCK]" in content_text:
                            actual_verdict = "BLOCK"
                            if expected_verdict == "BLOCK":
                                print(f"PASS: {mode_id} correctly blocked malicious content.")
                            else:
                                print(f"FAIL: {mode_id} falsely blocked clean content!")
                        else:
                            # Check audit.jsonl for exact verdict
                            actual_verdict = "ALLOW"
                            try:
                                with open("audit.jsonl", "r", encoding="utf-8") as audit_file:
                                    last_line = audit_file.readlines()[-1]
                                    last_entry = json.loads(last_line)
                                    if last_entry.get("verdict") == "ALLOW_DEGRADED":
                                        actual_verdict = "ALLOW_DEGRADED"
                            except Exception:
                                pass
                                
                            if expected_verdict == "ALLOW_DEGRADED":
                                if actual_verdict == "ALLOW_DEGRADED":
                                    print(f"PASS: {mode_id} correctly triggered DEGRADED fallback.")
                                else:
                                    print(f"FAIL: {mode_id} expected DEGRADED fallback but got {actual_verdict}!")
                            elif expected_verdict == "BLOCK":
                                print(f"FAIL: {mode_id} failed to block malicious content! (got {actual_verdict})")
                            else:
                                print(f"PASS: {mode_id} correctly allowed (verdict: {actual_verdict}).")
    except Exception as e:
        actual_verdict = "BLOCK" # Connection blocked or dropped
        if expected_verdict == "BLOCK":
            print(f"PASS: {mode_id} connection blocked as expected.")
        else:
            print(f"FAIL: {mode_id} connection failed unexpectedly: {e}")
            
    # Write to evaluation log
    with open("test_results.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "test_id": mode_id,
            "attack_class": attack_class,
            "expected_verdict": expected_verdict,
            "actual_verdict": actual_verdict
        }) + "\n")
        
    return actual_verdict == expected_verdict

async def main():
    # Clear audit log and state before starting
    for file in ["audit.jsonl", "rig_baseline.json", "rug_pull_state.txt", "test_results.jsonl"]:
        if os.path.exists(file):
            os.remove(file)

    tests = [
        # (mode_id, server_mode, expected_verdict, attack_class)
        ("layer4_test_1", "layer4_test_1", "BLOCK", "T6_SemanticInjection"),
        ("layer4_test_2", "layer4_test_2", "BLOCK", "T6_SemanticInjection"),
        ("layer4_test_3", "layer4_test_3", "BLOCK", "T6_SemanticInjection"),
        ("layer4_rate_limit_mock", "layer4_rate_limit_mock", "ALLOW_DEGRADED", "T6_SemanticInjection"),
        ("direct_poisoning", "direct_poisoning", "BLOCK", "T1_DirectPoisoning"),
        ("direct_poisoning_2", "direct_poisoning_2", "BLOCK", "T1_DirectPoisoning"),
        ("direct_poisoning_3", "direct_poisoning_3", "BLOCK", "T1_DirectPoisoning"),
        ("shadowing", "shadowing", "BLOCK", "T5_Shadowing"),
        ("shadowing_2", "shadowing_2", "BLOCK", "T5_Shadowing"),
        ("shadowing_3", "shadowing_3", "BLOCK", "T5_Shadowing"),
        ("rug_pull_1", "rug_pull_1", "ALLOW", "Clean"),
        ("rug_pull_2", "rug_pull_2", "BLOCK", "T4_RugPull"),
        ("rug_pull_3", "rug_pull_3", "BLOCK", "T4_RugPull"),
        ("rug_pull_4", "rug_pull_4", "BLOCK", "T4_RugPull"),
        ("output_injection_1", "output_injection_1", "BLOCK", "T3_OutputInjection"),
        ("output_injection_2", "output_injection_2", "BLOCK", "T3_OutputInjection"),
        ("output_injection_3", "output_injection_3", "BLOCK", "T3_OutputInjection"),
        ("output_injection_4", "output_injection_4", "BLOCK", "T3_OutputInjection"),
        ("output_injection_5", "output_injection_5", "BLOCK", "T3_OutputInjection"),
        ("output_injection_6", "output_injection_6", "BLOCK", "T3_OutputInjection"),
        ("output_injection_7", "output_injection_7", "BLOCK", "T3_OutputInjection"),
        ("output_injection_8", "output_injection_8", "BLOCK", "T3_OutputInjection"),
        ("layer4_benign_1", "layer4_benign_1", "ALLOW", "Clean"),
        ("layer4_benign_2", "layer4_benign_2", "ALLOW", "Clean"),
        ("clean_traffic_1", "clean_traffic_1", "ALLOW", "Clean"),
        ("clean_traffic_2", "clean_traffic_2", "ALLOW", "Clean"),
        ("clean_traffic_3", "clean_traffic_3", "ALLOW", "Clean"),
        ("clean_traffic_4", "clean_traffic_4", "ALLOW", "Clean"),
        ("clean_traffic_5", "clean_traffic_5", "ALLOW", "Clean"),
        ("clean_traffic_6", "clean_traffic_6", "ALLOW", "Clean"),
        ("clean_traffic_7", "clean_traffic_7", "ALLOW", "Clean"),
        ("clean_traffic_8", "clean_traffic_8", "ALLOW", "Clean"),
        ("clean_traffic_9", "clean_traffic_9", "ALLOW", "Clean"),
        ("clean_traffic_10", "clean_traffic_10", "ALLOW", "Clean"),
        ("clean_traffic_11", "clean_traffic_11", "ALLOW", "Clean"),
        ("clean_traffic_12", "clean_traffic_12", "ALLOW", "Clean"),
        ("clean_traffic_13", "clean_traffic_13", "ALLOW", "Clean"),
        ("clean_traffic_14", "clean_traffic_14", "ALLOW", "Clean"),
        ("clean_traffic_15", "clean_traffic_15", "ALLOW", "Clean"),
        ("clean_traffic_16", "clean_traffic_16", "ALLOW", "Clean"),
    ]
    
    all_passed = True
    for mode_id, server_mode, expected_verdict, attack_class in tests:
        passed = await run_test(mode_id, server_mode, expected_verdict, attack_class)
        if not passed:
            all_passed = False
        await asyncio.sleep(4.5)
        
    if all_passed:
        print("\nAll tests passed successfully!")
        sys.exit(0)
    else:
        print("\nSOME TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    if "--use-cache" in sys.argv:
        os.environ["USE_LLM_CACHE"] = "1"
        with open(".cached_run", "w") as f:
            f.write("1")
    else:
        if os.path.exists(".cached_run"):
            os.remove(".cached_run")
            
    asyncio.run(main())
