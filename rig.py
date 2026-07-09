import json
import hashlib
import os
import re

class RigEngine:
    def __init__(self, baseline_file="rig_baseline.json"):
        self.baseline_file = baseline_file
        self.baseline = self._load_baseline()
        
        # Layer 2 regex patterns
        self.patterns = [
            (re.compile(r"ignore previous instructions", re.IGNORECASE), "Instruction Override"),
            (re.compile(r"before executing,\s*read", re.IGNORECASE), "Instruction Override"),
            (re.compile(r"~/\.ssh|id_rsa|\.env|AWS_ACCESS_KEY", re.IGNORECASE), "Sensitive File/Credential Target"),
            (re.compile(r"[\u200B-\u200D\uFEFF]", re.IGNORECASE), "Zero-width characters (Obfuscation)"),
            (re.compile(r"secretly (BCC|forward|send)|exfiltrate", re.IGNORECASE), "Shadowing/Exfiltration Target"),
        ]

    def _load_baseline(self):
        if os.path.exists(self.baseline_file):
            with open(self.baseline_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_baseline(self):
        with open(self.baseline_file, 'w', encoding='utf-8') as f:
            json.dump(self.baseline, f, indent=2)

    def _hash_tool(self, tool):
        # Deterministic JSON dump
        tool_str = json.dumps(tool, sort_keys=True)
        return hashlib.sha256(tool_str.encode('utf-8')).hexdigest()

    def process_message(self, direction, msg):
        log_entry = {"direction": direction, "verdict": "ALLOW"}
        modified_msg = msg
        
        if direction == "server->client" and "result" in msg:
            result = msg["result"]
            
            # Layer 1: Hash Baseline & Layer 2: Descriptions
            if "tools" in result:
                new_tools = []
                for tool in result["tools"]:
                    tool_name = tool.get("name", "unknown")
                    tool_hash = self._hash_tool(tool)
                    
                    # Layer 1
                    if tool_name not in self.baseline:
                        self.baseline[tool_name] = tool_hash
                        self._save_baseline()
                    elif self.baseline[tool_name] != tool_hash:
                        log_entry["verdict"] = "BLOCK"
                        log_entry["reason"] = f"Layer 1: Rug-pull detected for tool '{tool_name}'"
                        # Block this tool by omitting it or flagging.
                        # For now, we omit it from new_tools if blocked
                        continue
                        
                    # Layer 2 on description/schema
                    tool_str = json.dumps(tool)
                    matched = False
                    for pattern, rule_name in self.patterns:
                        if pattern.search(tool_str):
                            log_entry["verdict"] = "BLOCK"
                            log_entry["reason"] = f"Layer 2: Pattern '{rule_name}' detected in tool '{tool_name}'"
                            matched = True
                            break
                            
                    if not matched:
                        new_tools.append(tool)
                        
                modified_msg["result"]["tools"] = new_tools
                if log_entry["verdict"] == "BLOCK":
                    # If we blocked tools, the log entry tells us.
                    pass
            
            # Layer 2: Output/return-value injection
            if "content" in result:
                content_str = json.dumps(result["content"])
                for pattern, rule_name in self.patterns:
                    if pattern.search(content_str):
                        log_entry["verdict"] = "BLOCK"
                        log_entry["reason"] = f"Layer 2: Pattern '{rule_name}' detected in tool output"
                        
                        # Replace the content with a safe substitute
                        modified_msg["result"]["content"] = [
                            {
                                "type": "text", 
                                "text": "[RIG BLOCK] Malicious payload detected in tool output."
                            }
                        ]
                        break

        log_entry["message"] = modified_msg
        return modified_msg, log_entry
