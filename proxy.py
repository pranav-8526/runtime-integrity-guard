import sys
import json
import argparse
import subprocess
import threading
from rig import RigEngine

engine = RigEngine()

def forward_stream(src_file, dst_file, name, log_file):
    for line in src_file:
        line_to_send = line
        # Intercept and log
        try:
            msg = json.loads(line.decode('utf-8'))
            modified_msg, log_entry = engine.process_message(name, msg)
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + "\n")
                
            line_to_send = (json.dumps(modified_msg) + "\n").encode('utf-8')
        except json.JSONDecodeError:
            pass
        except Exception as e:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"error": str(e), "direction": name}) + "\n")

        dst_file.write(line_to_send)
        dst_file.flush()

def main():
    parser = argparse.ArgumentParser(description="RIG Proxy")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run the real MCP server")
    args = parser.parse_args()

    log_file = "audit.jsonl"

    # Start child process
    process = subprocess.Popen(
        args.command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr
    )

    # Start forwarding threads
    t1 = threading.Thread(
        target=forward_stream,
        args=(sys.stdin.buffer, process.stdin, "client->server", log_file),
        daemon=True
    )
    t2 = threading.Thread(
        target=forward_stream,
        args=(process.stdout, sys.stdout.buffer, "server->client", log_file),
        daemon=True
    )

    t1.start()
    t2.start()

    process.wait()

if __name__ == "__main__":
    main()
