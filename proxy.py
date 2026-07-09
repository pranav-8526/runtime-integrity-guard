import sys
import os
import json
import argparse
import subprocess
import threading
from rig import RigEngine

def forward_stream(src_file, dst_file, name, log_file, engine):
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
            error_msg = f"RIG Engine crash on {name}: {e}"
            print(error_msg, file=sys.stderr)
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"error": str(e), "direction": name, "verdict": "BLOCK", "reason": "Engine crashed (Fail Closed)"}) + "\n")
            
            # Fail closed: Do not forward the original malicious message.
            if 'msg' in locals() and isinstance(msg, dict) and "id" in msg:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": msg["id"],
                    "error": {
                        "code": -32603,
                        "message": "Internal error: RIG proxy engine crashed."
                    }
                }
                error_bytes = (json.dumps(error_response) + "\n").encode('utf-8')
                if name == "server->client":
                    # For server->client, send the error back to the client via dst_file (which is sys.stdout.buffer)
                    line_to_send = error_bytes
                else:
                    # For client->server, dst_file is process.stdin. We must NOT send the error to the server.
                    # We send it directly back to the client via sys.stdout.buffer to resolve their request.
                    sys.stdout.buffer.write(error_bytes)
                    sys.stdout.buffer.flush()
                    continue
            else:
                continue  # Safest fallback is to drop the message entirely

        dst_file.write(line_to_send)
        dst_file.flush()
        
    try:
        dst_file.close()
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(description="RIG Proxy")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run the real MCP server")
    args = parser.parse_args()

    log_file = "audit.jsonl"

    # Derive a stable server_id using the absolute path to prevent collisions between different servers named 'app.py'
    if len(args.command) > 1 and any(runtime in args.command[0].lower() for runtime in ["python", "node", "ts-node"]):
        base_cmd = args.command[1]
    else:
        base_cmd = args.command[0]
    server_id = os.path.abspath(base_cmd)
    
    engine = RigEngine(server_id=server_id)

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
        args=(sys.stdin.buffer, process.stdin, "client->server", log_file, engine),
        daemon=True
    )
    t2 = threading.Thread(
        target=forward_stream,
        args=(process.stdout, sys.stdout.buffer, "server->client", log_file, engine),
        daemon=True
    )

    t1.start()
    t2.start()

    process.wait()

if __name__ == "__main__":
    main()