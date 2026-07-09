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
            self.send_header("Content-type", "text/html; charset=utf-8")
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
                <meta charset="UTF-8">
                <title>RIG Security Command Center</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
                <style>
                    :root {{
                        --bg-color: #030712;
                        --card-bg: rgba(17, 24, 39, 0.85);
                        --border-color: rgba(56, 189, 248, 0.2);
                        --cyan: #00f0ff;
                        --red: #ff3838;
                        --green: #00ff66;
                        --accent: #3b82f6;
                    }}
                    body {{ 
                        font-family: 'Outfit', sans-serif; 
                        background: var(--bg-color); 
                        background-image: 
                            radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0, transparent 50%),
                            radial-gradient(at 100% 100%, rgba(0, 240, 255, 0.08) 0, transparent 50%);
                        color: #f3f4f6; 
                        margin: 0; 
                        padding: 2rem; 
                        min-height: 100vh;
                        overflow-x: hidden;
                    }}
                    .container {{
                        max-width: 1000px;
                        margin: 0 auto;
                        position: relative;
                    }}
                    header {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 2.5rem;
                        border-bottom: 2px solid var(--border-color);
                        padding-bottom: 1.5rem;
                    }}
                    .logo-section h1 {{ 
                        font-family: 'Share Tech Mono', monospace;
                        color: var(--cyan); 
                        margin: 0;
                        font-size: 2.2rem;
                        text-transform: uppercase;
                        letter-spacing: 2px;
                        text-shadow: 0 0 10px rgba(0, 240, 255, 0.4);
                        display: flex;
                        align-items: center;
                        gap: 0.75rem;
                    }}
                    .logo-section p {{
                        margin: 0.25rem 0 0 0;
                        color: #6b7280;
                        font-size: 0.85rem;
                        letter-spacing: 1px;
                        text-transform: uppercase;
                    }}
                    .system-status {{
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                        font-family: 'Share Tech Mono', monospace;
                        font-size: 0.85rem;
                        background: rgba(0, 255, 102, 0.07);
                        border: 1px solid var(--green);
                        color: var(--green);
                        padding: 0.5rem 1rem;
                        border-radius: 4px;
                        box-shadow: 0 0 10px rgba(0, 255, 102, 0.15);
                        animation: pulseStatus 2s infinite alternate;
                    }}
                    @keyframes pulseStatus {{
                        0% {{ box-shadow: 0 0 5px rgba(0, 255, 102, 0.15); border-color: rgba(0, 255, 102, 0.5); }}
                        100% {{ box-shadow: 0 0 15px rgba(0, 255, 102, 0.4); border-color: var(--green); }}
                    }}
                    .card {{ 
                        background: var(--card-bg); 
                        border-radius: 8px; 
                        padding: 1.5rem; 
                        margin-bottom: 1.5rem; 
                        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
                        backdrop-filter: blur(8px);
                        border: 1px solid var(--border-color);
                        position: relative;
                        overflow: hidden;
                    }}
                    /* Cyberpunk HUD corners */
                    .card::before {{
                        content: "";
                        position: absolute;
                        top: 0; left: 0;
                        width: 8px; height: 8px;
                        border-top: 2px solid var(--cyan);
                        border-left: 2px solid var(--cyan);
                    }}
                    .card::after {{
                        content: "";
                        position: absolute;
                        bottom: 0; right: 0;
                        width: 8px; height: 8px;
                        border-bottom: 2px solid var(--cyan);
                        border-right: 2px solid var(--cyan);
                    }}
                    .stats {{ 
                        display: flex; 
                        gap: 1.5rem; 
                        justify-content: space-between; 
                    }}
                    .stat-box {{ 
                        text-align: center; 
                        background: rgba(17, 24, 39, 0.6); 
                        padding: 1.5rem; 
                        border-radius: 6px; 
                        flex: 1; 
                        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                        cursor: pointer;
                        border: 1px solid rgba(255, 255, 255, 0.03);
                        user-select: none;
                    }}
                    .stat-box:hover {{
                        transform: translateY(-4px);
                        border-color: rgba(0, 240, 255, 0.2);
                        background: rgba(17, 24, 39, 0.8);
                    }}
                    .stat-box.active {{
                        border-color: var(--cyan);
                        box-shadow: 0 0 15px rgba(0, 240, 255, 0.25);
                        background: rgba(0, 240, 255, 0.05);
                    }}
                    .stat-box.active-blocked {{
                        border-color: var(--red);
                        box-shadow: 0 0 15px rgba(255, 56, 56, 0.25);
                        background: rgba(255, 56, 56, 0.05);
                    }}
                    .stat-box.active-allowed {{
                        border-color: var(--green);
                        box-shadow: 0 0 15px rgba(0, 255, 102, 0.25);
                        background: rgba(0, 255, 102, 0.05);
                    }}
                    .stat-number {{ 
                        font-family: 'Share Tech Mono', monospace;
                        font-size: 2.8rem; 
                        font-weight: bold; 
                        color: var(--cyan); 
                        margin-bottom: 0.25rem;
                        text-shadow: 0 0 8px rgba(0, 240, 255, 0.2);
                    }}
                    .blocked {{ 
                        color: var(--red) !important;
                        text-shadow: 0 0 8px rgba(255, 56, 56, 0.2) !important;
                    }}
                    .allowed {{ 
                        color: var(--green) !important;
                        text-shadow: 0 0 8px rgba(0, 255, 102, 0.2) !important;
                    }}
                    
                    table {{ 
                        width: 100%; 
                        border-collapse: collapse; 
                        margin-top: 1rem; 
                    }}
                    th, td {{ 
                        padding: 1rem; 
                        text-align: left; 
                        border-bottom: 1px solid rgba(255, 255, 255, 0.05); 
                    }}
                    th {{ 
                        font-family: 'Share Tech Mono', monospace;
                        color: #9ca3af; 
                        text-transform: uppercase;
                        font-size: 0.85rem;
                        letter-spacing: 0.05em;
                    }}
                    tr.log-row {{ 
                        cursor: pointer; 
                        transition: all 0.2s ease;
                    }}
                    tr.log-row:hover {{ 
                        background: rgba(255, 255, 255, 0.02); 
                    }}
                    .badge {{
                        font-family: 'Share Tech Mono', monospace;
                        padding: 0.3rem 0.75rem; 
                        border-radius: 4px; 
                        font-size: 0.8rem;
                        font-weight: bold;
                        letter-spacing: 0.05em;
                        display: inline-block;
                    }}
                    .badge-ALLOW {{ 
                        background: rgba(0, 255, 102, 0.1); 
                        color: var(--green); 
                        border: 1px solid rgba(0, 255, 102, 0.2);
                    }}
                    .badge-BLOCK {{ 
                        background: rgba(255, 56, 56, 0.1); 
                        color: var(--red); 
                        border: 1px solid rgba(255, 56, 56, 0.2);
                    }}
                    .reason-text {{ color: #cbd5e1; font-family: monospace; font-size: 0.9rem; }}
                    
                    @keyframes expandDrawer {{
                        from {{ opacity: 0; transform: translateY(-8px); }}
                        to {{ opacity: 1; transform: translateY(0); }}
                    }}
                    .detail-container {{
                        display: flex;
                        flex-direction: column;
                        gap: 1rem;
                        animation: expandDrawer 0.25s cubic-bezier(0.4, 0, 0.2, 1) forwards;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <header>
                        <div class="logo-section">
                            <h1>🛡️ RIG Command Center</h1>
                            <p>Runtime Integrity Guard Security System</p>
                        </div>
                        <div class="system-status">
                            <span style="width: 8px; height: 8px; background: var(--green); border-radius: 50%; display: inline-block; box-shadow: 0 0 8px var(--green);"></span>
                            SECURE - MONITORING ACTIVE
                        </div>
                    </header>
            """
            
            total = len(logs)
            blocked = sum(1 for log in logs if log.get("verdict") == "BLOCK")
            allowed = total - blocked
            
            html_content += f"""
                    <div class="card stats">
                        <div class="stat-box active" id="stat-total" onclick="filterLogs('all')">
                            <div class="stat-number">{total}</div>
                            <div style="color: #9ca3af; font-weight: 500; font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; text-transform: uppercase;">Total Messages</div>
                        </div>
                        <div class="stat-box" id="stat-blocked" onclick="filterLogs('BLOCK')">
                            <div class="stat-number blocked">{blocked}</div>
                            <div style="color: #9ca3af; font-weight: 500; font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; text-transform: uppercase;">Threats Blocked</div>
                        </div>
                        <div class="stat-box" id="stat-allowed" onclick="filterLogs('ALLOW')">
                            <div class="stat-number allowed">{allowed}</div>
                            <div style="color: #9ca3af; font-weight: 500; font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; text-transform: uppercase;">Safe Messages</div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h2 style="margin-top: 0; color: #f1f5f9; font-family: 'Share Tech Mono', monospace; letter-spacing: 1px; font-size: 1.3rem;">[ RECENT AUDIT LOGS ]</h2>
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
                                <td colspan="3" style="text-align: center; color: #94a3b8; padding: 2.5rem; font-family: 'Share Tech Mono', monospace;">NO ACTIVE LOG STREAMS DETECTED. RUN SYSTEM TRAFFIC...</td>
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
                        explanation = f"RIG mitigation engine triggered hard block: {reason}."
                    else:
                        # Scan raw message for suspicious words to calculate confidence
                        msg_str = json.dumps(log.get('message', {}), ensure_ascii=False).lower()
                        suspicious_terms = ["ssh", "env", "key", "password", "token", "secret", "override", "instruction", "exfiltrate", "dump", "export"]
                        matched_terms = [t for t in suspicious_terms if t in msg_str]
                        if matched_terms:
                            score = min(90, 10 + len(matched_terms) * 10)
                            explanation = f"Inspection completed: Traffic allowed, but detected suspicious cyber context terms ({', '.join(matched_terms)}). Monitoring payload closely."
                        else:
                            score = 5
                            explanation = "Inspection completed: Safe baseline traffic validated. Zero threat indicators found."
                            
                    # Prettify raw JSON payload
                    raw_msg_json = json.dumps(log.get('message', {}), indent=2, ensure_ascii=False)
                    escaped_json = html.escape(raw_msg_json)
                    
                    html_content += f"""
                            <tr class="log-row" data-verdict="{verdict}" data-index="{idx}" onclick="toggleDetails({idx})">
                                <td><span style="color: #94a3b8; font-family: 'Share Tech Mono', monospace;">{direction}</span></td>
                                <td><span class="badge badge-{verdict}">{verdict}</span></td>
                                <td class="reason-text">{reason}</td>
                            </tr>
                            <tr class="detail-row" id="details-{idx}" style="display: none; background: rgba(15, 23, 42, 0.65);">
                                <td colspan="3" style="padding: 1.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                                    <div class="detail-container">
                                        <div style="display: flex; justify-content: space-between; align-items: center;">
                                            <strong style="color: #f1f5f9; font-family: 'Share Tech Mono', monospace; font-size: 0.95rem; letter-spacing: 1px;">🔍 SECURITY INTELLIGENCE ANALYSIS</strong>
                                            <span class="badge" style="background: rgba(0, 240, 255, 0.1); color: var(--cyan); border: 1px solid rgba(0, 240, 255, 0.2);">
                                                MALICIOUS CONFIDENCE: {score}%
                                            </span>
                                        </div>
                                        <p style="margin: 0; color: #94a3b8; font-size: 0.95rem; line-height: 1.5;">{explanation}</p>
                                        <div style="background: #020617; border-radius: 4px; padding: 1.25rem; border: 1px solid rgba(255, 255, 255, 0.08); margin-top: 0.5rem; position: relative;">
                                            <span style="font-size: 0.7rem; color: #6b7280; font-family: 'Share Tech Mono', monospace; text-transform: uppercase; letter-spacing: 0.1rem; display: block; margin-bottom: 0.5rem;">[ INTERCEPTED DATA STREAM ]</span>
                                            <pre style="margin: 0; color: var(--cyan); font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; max-height: 250px;">{escaped_json}</pre>
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
                            // Smooth animation trigger
                            const detailContainer = detailsRow.querySelector('.detail-container');
                            if (detailContainer) {
                                detailContainer.style.animation = 'none';
                                detailContainer.offsetHeight; /* trigger reflow */
                                detailContainer.style.animation = null;
                            }
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