import http.server
import socketserver
import json
import os
import html

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
            html_content = f"""
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
                        transition: all 0.2s;
                        cursor: pointer;
                        border: 2px solid transparent;
                        user-select: none;
                    }}
                    .stat-box:hover {{
                        transform: translateY(-5px);
                    }}
                    .stat-box.active {{
                        border-color: #38bdf8;
                        background: #1e293b;
                    }}
                    .stat-box.active-blocked {{
                        border-color: #ef4444;
                        background: #1e293b;
                    }}
                    .stat-box.active-allowed {{
                        border-color: #22c55e;
                        background: #1e293b;
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
                    tr.log-row {{ cursor: pointer; }}
                    tr.log-row:hover {{ background: #334155; }}
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
            
            html_content += f"""
                    <div class="card stats">
                        <div class="stat-box active" id="stat-total" onclick="filterLogs('all')">
                            <div class="stat-number">{total}</div>
                            <div style="color: #94a3b8; font-weight: 500;">Total Messages</div>
                        </div>
                        <div class="stat-box" id="stat-blocked" onclick="filterLogs('BLOCK')">
                            <div class="stat-number blocked">{blocked}</div>
                            <div style="color: #94a3b8; font-weight: 500;">Threats Blocked</div>
                        </div>
                        <div class="stat-box" id="stat-allowed" onclick="filterLogs('ALLOW')">
                            <div class="stat-number allowed">{allowed}</div>
                            <div style="color: #94a3b8; font-weight: 500;">Safe Messages</div>
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
                html_content += """
                            <tr>
                                <td colspan="3" style="text-align: center; color: #94a3b8; padding: 2rem;">No logs found yet. Run the tests to generate traffic!</td>
                            </tr>
                """
            else:
                for idx, log in enumerate(reversed(logs[-30:])): # Show last 30
                    verdict = html.escape(str(log.get('verdict', 'UNKNOWN')))
                    
                    # Handle both 'reason' (string) and 'reasons' (list) for future-proofing Fix 7
                    raw_reason = log.get('reasons', log.get('reason', []))
                    if isinstance(raw_reason, list):
                        raw_reason = " | ".join(raw_reason) if raw_reason else "Safe traffic passed without modification."
                    if not raw_reason:
                        raw_reason = "Safe traffic passed without modification."
                    reason = html.escape(str(raw_reason))
                    
                    direction = html.escape(str(log.get('direction', '-')))
                    
                    # Calculate Malicious Confidence Score & Detailed Explanation
                    score = 0
                    explanation = ""
                    
                    if verdict == "BLOCK":
                        score = 100
                        explanation = f"Critically blocked by RIG proxy engine. Reason: {reason}."
                    else:
                        # Scan raw message for suspicious words to calculate confidence
                        msg_str = json.dumps(log.get('message', {}), ensure_ascii=False).lower()
                        suspicious_terms = ["ssh", "env", "key", "password", "token", "secret", "override", "instruction", "exfiltrate", "dump", "export"]
                        matched_terms = [t for t in suspicious_terms if t in msg_str]
                        if matched_terms:
                            score = min(90, 10 + len(matched_terms) * 10)
                            explanation = f"Traffic allowed, but contains suspicious term(s) ({', '.join(matched_terms)}). Minor background risk detected."
                        else:
                            score = 5
                            explanation = "Clean baseline traffic verified. No malicious indicators found."
                            
                    # Prettify raw JSON payload
                    raw_msg_json = json.dumps(log.get('message', {}), indent=2, ensure_ascii=False)
                    escaped_json = html.escape(raw_msg_json)
                    
                    html_content += f"""
                            <tr class="log-row" data-verdict="{verdict}" data-index="{idx}" onclick="toggleDetails({idx})">
                                <td><span style="color: #94a3b8">{direction}</span></td>
                                <td><span class="badge badge-{verdict}">{verdict}</span></td>
                                <td class="reason-text">{reason}</td>
                            </tr>
                            <tr class="detail-row" id="details-{idx}" style="display: none; background: #1e293b;">
                                <td colspan="3" style="padding: 1.5rem; border-bottom: 1px solid #334155;">
                                    <div style="display: flex; flex-direction: column; gap: 1rem;">
                                        <div style="display: flex; justify-content: space-between; align-items: center;">
                                            <strong style="color: #f1f5f9;">🔍 Security Analysis & Breakdown</strong>
                                            <span class="badge" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3);">
                                                Malicious Confidence: {score}%
                                            </span>
                                        </div>
                                        <p style="margin: 0; color: #94a3b8; font-size: 0.95rem; line-height: 1.5;">{explanation}</p>
                                        <div style="background: #0f172a; border-radius: 8px; padding: 1rem; border: 1px solid #334155; margin-top: 0.5rem;">
                                            <span style="font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 0.5rem;">Raw Intercepted JSON Payload</span>
                                            <pre style="margin: 0; color: #38bdf8; font-family: monospace; font-size: 0.85rem; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; max-height: 250px;">{escaped_json}</pre>
                                        </div>
                                    </div>
                                </td>
                            </tr>
                    """
                
            html_content += """
                        </table>
                    </div>
                </div>
                <script>
                    function filterLogs(filterType) {
                        // 1. Reset all active states on stat boxes
                        document.getElementById('stat-total').classList.remove('active');
                        document.getElementById('stat-blocked').classList.remove('active-blocked');
                        document.getElementById('stat-allowed').classList.remove('active-allowed');
                        
                        // 2. Add active class to clicked box
                        if (filterType === 'all') {
                            document.getElementById('stat-total').classList.add('active');
                        } else if (filterType === 'BLOCK') {
                            document.getElementById('stat-blocked').classList.add('active-blocked');
                        } else if (filterType === 'ALLOW') {
                            document.getElementById('stat-allowed').classList.add('active-allowed');
                        }
                        
                        // 3. Show/hide table rows
                        const rows = document.querySelectorAll('.log-row');
                        rows.forEach(row => {
                            const rowVerdict = row.getAttribute('data-verdict');
                            const idx = row.getAttribute('data-index');
                            const detailRow = document.getElementById('details-' + idx);
                            if (filterType === 'all' || rowVerdict === filterType) {
                                row.style.display = '';
                            } else {
                                row.style.display = 'none';
                                if (detailRow) detailRow.style.display = 'none';
                            }
                        });
                    }
                    
                    function toggleDetails(index) {
                        const detailsRow = document.getElementById('details-' + index);
                        if (detailsRow.style.display === 'none') {
                            detailsRow.style.display = 'table-row';
                        } else {
                            detailsRow.style.display = 'none';
                        }
                    }
                </script>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode("utf-8"))
        else:
            self.send_error(404, "Not Found")

if __name__ == "__main__":
    print(f"Starting dashboard server...")
    print(f"Access your dashboard at: http://127.0.0.1:{PORT}")
    try:
        with socketserver.TCPServer(("127.0.0.1", PORT), RIGDashboardHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
    except Exception as e:
        print(f"Error starting server: {e}")