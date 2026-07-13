import asyncio
import json
import os
import sys
from rig import RigEngine
import test_servers.suite as suite

async def run_direct_test(mode_id, server_mode, expected_verdict, attack_class, engine):
    print(f"\n--- Running Test Mode: {mode_id} ---")
    suite.server_mode = server_mode
    
    # 1. Simulate tool listing
    tools = await suite.list_tools()
    tools_serialized = []
    for tool in tools:
        if hasattr(tool, "model_dump"):
            tools_serialized.append(tool.model_dump())
        elif hasattr(tool, "dict"):
            tools_serialized.append(tool.dict())
        else:
            tools_serialized.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            })
            
    listing_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "tools": tools_serialized
        }
    }
    
    actual_verdict = "ALLOW"
    modified_msg, log_entry = engine.process_message("server->client", listing_msg)
    
    # Write to audit log
    with open("audit.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
        
    if log_entry["verdict"] == "BLOCK":
        actual_verdict = "BLOCK"
        if expected_verdict == "BLOCK":
            print(f"PASS: {mode_id} correctly blocked at schema level.")
        else:
            print(f"FAIL: {mode_id} falsely blocked at schema level!")
    else:
        # Schema allowed, now call tool if output injection/clean
        schema_blocked_modes = ["direct_poisoning", "shadowing", "rug_pull_2", "rug_pull_3", "rug_pull_4"]
        if mode_id in schema_blocked_modes:
            actual_verdict = "ALLOW"
            print(f"FAIL: {mode_id} expected schema block but was allowed!")
        else:
            tool_name = tools_serialized[0]["name"]
            print(f"Calling tool: {tool_name}")
            
            contents = await suite.call_tool(tool_name, {})
            contents_serialized = []
            for content in contents:
                if hasattr(content, "model_dump"):
                    contents_serialized.append(content.model_dump())
                elif hasattr(content, "dict"):
                    contents_serialized.append(content.dict())
                else:
                    contents_serialized.append({
                        "type": content.type,
                        "text": content.text
                    })
                    
            call_msg = {
                "jsonrpc": "2.0",
                "id": 2,
                "result": {
                    "content": contents_serialized
                }
            }
            
            modified_call_msg, call_log_entry = engine.process_message("server->client", call_msg)
            
            # Write to audit log
            with open("audit.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(call_log_entry) + "\n")
                
            if call_log_entry["verdict"] == "BLOCK":
                actual_verdict = "BLOCK"
                if expected_verdict == "BLOCK":
                    print(f"PASS: {mode_id} correctly blocked malicious content.")
                else:
                    print(f"FAIL: {mode_id} falsely blocked clean content!")
            else:
                actual_verdict = "ALLOW"
                if expected_verdict == "BLOCK":
                    print(f"FAIL: {mode_id} failed to block malicious content!")
                else:
                    print(f"PASS: {mode_id} correctly allowed.")
                    
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
    # Clear logs and baseline before starting
    for file in ["audit.jsonl", "rig_baseline.json", "rug_pull_state.txt", "test_results.jsonl"]:
        if os.path.exists(file):
            os.remove(file)
            
    engine = RigEngine(server_id="test_suite")
    
    tests = [
        # (mode_id, server_mode, expected_verdict, attack_class)
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
        passed = await run_direct_test(mode_id, server_mode, expected_verdict, attack_class, engine)
        if not passed:
            all_passed = False
            
    print("\n=======================================================")
    print("Execution Finished. Printing report summary:")
    print("=======================================================\n")
    
    from rig_report import generate_report, evaluate_results
    generate_report("audit.jsonl")
    evaluate_results("test_results.jsonl")

if __name__ == "__main__":
    asyncio.run(main())
