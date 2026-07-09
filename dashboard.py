import http.server
import socketserver
import json
import os

PORT = 3000

class RIGDashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            # Read audit.jsonl
            logs = []
            if os.path.exists("audit.jsonl"):
                with open("audit.jsonl", "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            try:
                                logs.append(json.loads(line))
                            except:
                                pass
                                
            # Build HTML
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>RIG Security Dashboard</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                        background: #0f172a; 
                        color: #f8fafc; 
                        margin: 0; 
                        padding: 2rem; 
                    }}
                    .container {{
                        max-width: 1000px;
                        margin: 0 auto;
                    }}
                    h1 {{ 
                        color: #38bdf8; 
                        text-align: center; 
                        margin-bottom: 2rem;
                    }}
                    .card {{ 
                        background: #1e293b; 
                        border-radius: 12px; 
                        padding: 1.5rem; 
                        margin-bottom: 1.5rem; 
                        box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
                        border: 1px solid #334155;
                    }}
                    .stats {{ 
                        display: flex; 
                        gap: 1.5rem; 
                        justify-content: space-between; 
                    }}
                    .stat-box {{ 
                        text-align: center; 
                        background: #334155; 
                        padding: 1.5rem; 
                        border-radius: 12px; 
                        flex: 1; 
                        transition: transform 0.2s;
                    }}
                    .stat-box:hover {{
                        transform: translateY(-5px);
                    }}
                    .stat-number {{ 
                        font-size: 2.5rem; 
                        font-weight: bold; 
                        color: #38bdf8; 
                        margin-bottom: 0.5rem;
                    }}
                    .blocked {{ color: #ef4444; }}
                    .allowed {{ color: #22c55e; }}
                    
                    table {{ 
                        width: 100%; 
                        border-collapse: collapse; 
                        margin-top: 1rem; 
                    }}
                    th, td {{ 
                        padding: 1rem; 
                        text-align: left; 
                        border-bottom: 1px solid #334155; 
                    }}
                    th {{ 
                        color: #94a3b8; 
                        text-transform: uppercase;
                        font-size: 0.85rem;
                        letter-spacing: 0.05em;
                    }}
                    tr:hover {{ background: #334155; }}
                    .badge {{
                        padding: 0.35rem 0.75rem; 
                        border-radius: 9999px; 
                        font-size: 0.8rem;
                        font-weight: 600;
                    }}
                    .badge-ALLOW {{ background: rgba(34, 197, 94, 0.2); color: #4ade80; }}
                    .badge-BLOCK {{ background: rgba(239, 68, 68, 0.2); color: #f87171; }}
                    .reason-text {{ color: #cbd5e1; font-family: monospace; font-size: 0.9rem; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🛡️ Runtime Integrity Guard Dashboard</h1>
            """
            
            total = len(logs)
            blocked = sum(1 for log in logs if log.get("verdict") == "BLOCK")
            allowed = total - blocked
            
            html += f"""
                    <div class="card stats">
                        <div class="stat-box">
                            <div class="stat-number">{total}</div>
                            <div style="color: #94a3b8">Total Messages</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number blocked">{blocked}</div>
                            <div style="color: #94a3b8">Threats Blocked</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number allowed">{allowed}</div>
                            <div style="color: #94a3b8">Safe Messages</div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h2 style="margin-top: 0; color: #f1f5f9;">Recent Audit Logs</h2>
                        <table>
                            <tr>
                                <th>Direction</th>
                                <th>Verdict</th>
                                <th>Action / Reason</th>
                            </tr>
            """
            
            if not logs:
                html += """
                            <tr>
                                <td colspan="3" style="text-align: center; color: #94a3b8; padding: 2rem;">No logs found yet. Run the tests to generate traffic!</td>
                            </tr>
                """
            else:
                for log in reversed(logs[-30:]): # Show last 30
                    verdict = log.get('verdict', 'UNKNOWN')
                    reason = log.get('reason', 'Safe traffic passed without modification.')
                    direction = log.get('direction', '-')
                    html += f"""
                            <tr>
                                <td><span style="color: #94a3b8">{direction}</span></td>
                                <td><span class="badge badge-{verdict}">{verdict}</span></td>
                                <td class="reason-text">{reason}</td>
                            </tr>
                    """
                
            html += """
                        </table>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
        else:
            super().do_GET()

if __name__ == "__main__":
    print(f"Starting dashboard server...")
    print(f"Access your dashboard at: http://localhost:{PORT}")
    try:
        with socketserver.TCPServer(("", PORT), RIGDashboardHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
    except Exception as e:
        print(f"Error starting server: {e}")