import json
import argparse

def generate_report(log_file):
    total_messages = 0
    blocked_messages = 0
    reasons = {}
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    total_messages += 1
                    
                    if entry.get("verdict") == "BLOCK":
                        blocked_messages += 1
                        reason = entry.get("reason", "Unknown Reason")
                        reasons[reason] = reasons.get(reason, 0) + 1
                except json.JSONDecodeError:
                    pass
    except FileNotFoundError:
        print(f"Log file {log_file} not found.")
        return

    print("=========================================")
    print("      RIG Security Audit Report          ")
    print("=========================================")
    print(f"Total Messages Inspected: {total_messages}")
    print(f"Total Messages Blocked:   {blocked_messages}")
    print("\nBreakdown by Detection Class:")
    for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {reason}: {count}")
    print("=========================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate RIG Audit Report")
    parser.add_argument("--log", default="audit.jsonl", help="Path to JSONL audit log")
    args = parser.parse_args()
    
    generate_report(args.log)