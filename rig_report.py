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
                        
                        raw_reason = entry.get("reasons", entry.get("reason", "Unknown Reason"))
                        if isinstance(raw_reason, list):
                            for r in raw_reason:
                                reasons[r] = reasons.get(r, 0) + 1
                        else:
                            reasons[raw_reason] = reasons.get(raw_reason, 0) + 1
                except json.JSONDecodeError:
                    pass
    except FileNotFoundError:
        print(f"Log file {log_file} not found.")
        return

    print("=========================================")
    print("      RIG Security Audit Report          ")
    print("=========================================")
    print(f"Total Messages Inspected: {total_messages}")
    print("  *(Note: Counts all JSON-RPC stream packets including handshakes and tool-listing, not just test cases)")
    print(f"Total Messages Blocked:   {blocked_messages}")
    print("\nBreakdown by Detection Class:")
    for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {reason}: {count}")
    print("=========================================")

    print("=========================================")

def evaluate_results(results_file):
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Results file {results_file} not found.")
        return

    metrics = {}
    
    for line in lines:
        if not line.strip(): continue
        try:
            entry = json.loads(line)
        except:
            continue
            
        ac = entry.get("attack_class", "Unknown")
        expected = entry.get("expected_verdict")
        actual = entry.get("actual_verdict")
        
        if ac not in metrics:
            metrics[ac] = {"TP": 0, "FP": 0, "TN": 0, "FN": 0}
            
        if expected == "BLOCK" and actual == "BLOCK":
            metrics[ac]["TP"] += 1
        elif expected == "ALLOW" and actual == "BLOCK":
            metrics[ac]["FP"] += 1
        elif expected == "ALLOW" and actual == "ALLOW":
            metrics[ac]["TN"] += 1
        elif expected == "BLOCK" and actual == "ALLOW":
            metrics[ac]["FN"] += 1

    print("\n=========================================================================")
    print("                 RIG Evaluation Metrics                                  ")
    print("=========================================================================")
    print(f"{'Attack Class':<20} | {'TP':<4} | {'FP':<4} | {'TN':<4} | {'FN':<4} | {'Recall':<8} | {'Precision':<9} | {'FPR':<8}")
    print("-" * 75)
    
    for ac, m in sorted(metrics.items()):
        tp, fp, tn, fn = m["TP"], m["FP"], m["TN"], m["FN"]
        
        recall = f"{tp / (tp + fn):.2f}" if (tp + fn) > 0 else "N/A"
        precision = f"{tp / (tp + fp):.2f}" if (tp + fp) > 0 else "N/A"
        fpr = f"{fp / (fp + tn):.2f}" if (fp + tn) > 0 else "N/A"
        
        print(f"{ac:<20} | {tp:<4} | {fp:<4} | {tn:<4} | {fn:<4} | {recall:<8} | {precision:<9} | {fpr:<8}")
    print("=========================================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate RIG Audit Report")
    parser.add_argument("--log", default="audit.jsonl", help="Path to JSONL audit log")
    parser.add_argument("--results", default="test_results.jsonl", help="Path to JSONL test results")
    args = parser.parse_args()
    
    generate_report(args.log)
    evaluate_results(args.results)
