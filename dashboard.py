import http.server
import socketserver
import json
import os
import html

PORT = 3001

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
                                
            # Pre-serialize logs to JS format for the modal lookup
            recent_logs = list(reversed(logs[-30:]))
            logs_js_json = json.dumps(recent_logs)
            
            # Build HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>RIG Tactical Command Center</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
                <style>
                    :root {{
                        --bg-color: #020202;
                        --card-bg: rgba(8, 8, 8, 0.25);
                        --border-color: rgba(255, 85, 0, 0.25);
                        --orange: #ff5500;
                        --red: #ff2222;
                        --muted-orange: rgba(255, 85, 0, 0.15);
                        --muted-red: rgba(255, 34, 34, 0.15);
                        --text-color: #e4e4e7;
                    }}
                    html, body {{
                        margin: 0;
                        padding: 0;
                        background: var(--bg-color);
                        overflow-x: hidden;
                    }}
                    body {{ 
                        font-family: 'Outfit', sans-serif; 
                        color: var(--text-color); 
                        padding: 2rem 2rem 3rem 2rem; 
                        min-height: 100vh;
                        position: relative;
                        perspective: 1200px; /* Enable 3D perspective */
                        box-sizing: border-box;
                    }}
                    
                    /* Parallax Background Layers */
                    #bg-grid-1 {{
                        position: fixed;
                        top: -20%; left: -20%; width: 140%; height: 140%;
                        background-image: 
                            linear-gradient(rgba(255, 85, 0, 0.05) 1px, transparent 1px),
                            linear-gradient(90deg, rgba(255, 85, 0, 0.05) 1px, transparent 1px);
                        background-size: 60px 60px;
                        z-index: 1;
                        pointer-events: none;
                        will-change: transform;
                    }}
                    #bg-grid-2 {{
                        position: fixed;
                        top: -20%; left: -20%; width: 140%; height: 140%;
                        background-image: 
                            radial-gradient(rgba(255, 34, 34, 0.06) 2px, transparent 2px);
                        background-size: 80px 80px;
                        z-index: 2;
                        pointer-events: none;
                        will-change: transform;
                    }}
                    
                    /* Vector Shield Background (3D Y-axis Rotation) */
                    #bg-shield {{
                        position: fixed;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%) rotateY(0deg);
                        width: 55vw;
                        height: 55vw;
                        max-width: 650px;
                        max-height: 650px;
                        opacity: 0.58;
                        z-index: 3;
                        pointer-events: none;
                        will-change: transform;
                        filter: drop-shadow(0 0 35px rgba(255, 85, 0, 0.45));
                        transform-style: preserve-3d;
                    }}
                    
                    /* Scanning Red Rays */
                    .red-ray-1 {{
                        position: fixed;
                        top: 0; left: 15%; width: 2px; height: 100%;
                        background: linear-gradient(180deg, transparent, rgba(255, 34, 34, 0.2) 30%, rgba(255, 34, 34, 0.2) 70%, transparent);
                        z-index: 4;
                        pointer-events: none;
                    }}
                    .red-ray-2 {{
                        position: fixed;
                        top: 0; right: 20%; width: 1px; height: 100%;
                        background: linear-gradient(180deg, transparent, rgba(255, 34, 34, 0.15) 10%, rgba(255, 34, 34, 0.25) 60%, transparent);
                        z-index: 4;
                        pointer-events: none;
                    }}
                    
                    /* Horizontal Wave Lines sweeping left-to-right end */
                    .wave-line {{
                        position: fixed;
                        left: 0; right: 0;
                        height: 2px;
                        background: linear-gradient(90deg, transparent, rgba(255, 85, 0, 0.25), rgba(255, 34, 34, 0.45), rgba(255, 85, 0, 0.25), transparent);
                        z-index: 6;
                        pointer-events: none;
                        animation: sweep 8s linear infinite;
                    }}
                    @keyframes sweep {{
                        0% {{ transform: translateY(-10vh); opacity: 0; }}
                        10% {{ opacity: 1; }}
                        90% {{ opacity: 1; }}
                        100% {{ transform: translateY(110vh); opacity: 0; }}
                    }}
                    
                    /* Floating Orange Tactical Target Dots */
                    .target-dot {{
                        position: fixed;
                        width: 5px;
                        height: 5px;
                        background: var(--orange);
                        border-radius: 50%;
                        box-shadow: 0 0 8px var(--orange);
                        z-index: 5;
                        pointer-events: none;
                        opacity: 0.7;
                        animation: pulseDot 2.2s infinite alternate;
                    }}
                    @keyframes pulseDot {{
                        0% {{ transform: scale(0.8); opacity: 0.3; }}
                        100% {{ transform: scale(1.5); opacity: 0.95; }}
                    }}
                    
                    .container {{
                        max-width: 1000px;
                        margin: 0 auto;
                        position: relative;
                        z-index: 10;
                    }}
                    header {{
                        display: flex;
                        justify-content: flex-start;
                        align-items: center;
                        margin-bottom: 2.5rem;
                        border-bottom: 2px solid var(--border-color);
                        padding-bottom: 1.5rem;
                        gap: 2rem;
                    }}
                    .logo-section h1 {{ 
                        font-family: 'Share Tech Mono', monospace;
                        color: var(--orange); 
                        margin: 0;
                        font-size: 2.2rem;
                        text-transform: uppercase;
                        letter-spacing: 2px;
                        text-shadow: 0 0 10px rgba(255, 85, 0, 0.4);
                        text-align: left;
                    }}
                    .logo-section p {{
                        margin: 0.25rem 0 0 0;
                        color: #71717a;
                        font-size: 0.85rem;
                        letter-spacing: 1.5px;
                        text-transform: uppercase;
                        text-align: left;
                    }}
                    .system-status {{
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                        font-family: 'Share Tech Mono', monospace;
                        font-size: 0.85rem;
                        background: rgba(255, 85, 0, 0.07);
                        border: 1px solid var(--orange);
                        color: var(--orange);
                        padding: 0.5rem 1rem;
                        border-radius: 4px;
                        box-shadow: 0 0 10px rgba(255, 85, 0, 0.15);
                        animation: pulseStatus 2.5s infinite alternate;
                        margin-left: auto;
                    }}
                    @keyframes pulseStatus {{
                        0% {{ box-shadow: 0 0 5px rgba(255, 85, 0, 0.15); border-color: rgba(255, 85, 0, 0.4); }}
                        100% {{ box-shadow: 0 0 15px rgba(255, 85, 0, 0.4); border-color: var(--orange); }}
                    }}
                    .card {{ 
                        background: var(--card-bg); 
                        border-radius: 4px; 
                        padding: 1.5rem; 
                        margin-bottom: 1.5rem; 
                        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
                        backdrop-filter: blur(10px);
                        border: 1px solid var(--border-color);
                        position: relative;
                    }}
                    /* Cyberpunk HUD corners */
                    .card::before {{
                        content: "";
                        position: absolute;
                        top: -1px; left: -1px;
                        width: 8px; height: 8px;
                        border-top: 2px solid var(--orange);
                        border-left: 2px solid var(--orange);
                    }}
                    .card::after {{
                        content: "";
                        position: absolute;
                        bottom: -1px; right: -1px;
                        width: 8px; height: 8px;
                        border-bottom: 2px solid var(--orange);
                        border-right: 2px solid var(--orange);
                    }}
                    .stats {{ 
                        display: flex; 
                        gap: 1.5rem; 
                        justify-content: space-between; 
                    }}
                    .stat-box {{ 
                        text-align: center; 
                        background: rgba(15, 15, 15, 0.5); 
                        padding: 1.5rem; 
                        border-radius: 4px; 
                        flex: 1; 
                        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                        cursor: pointer;
                        border: 1px solid rgba(255, 255, 255, 0.02);
                        user-select: none;
                    }}
                    .stat-box:hover {{
                        transform: translateY(-4px);
                        border-color: rgba(255, 85, 0, 0.3);
                        background: rgba(25, 25, 25, 0.6);
                    }}
                    .stat-box.active {{
                        border-color: var(--orange);
                        box-shadow: 0 0 15px rgba(255, 85, 0, 0.25);
                        background: rgba(255, 85, 0, 0.05);
                    }}
                    .stat-box.active-blocked {{
                        border-color: var(--red);
                        box-shadow: 0 0 15px rgba(255, 34, 34, 0.25);
                        background: rgba(255, 34, 34, 0.05);
                    }}
                    .stat-box.active-allowed {{
                        border-color: var(--orange);
                        box-shadow: 0 0 15px rgba(255, 85, 0, 0.2);
                        background: rgba(255, 85, 0, 0.03);
                    }}
                    .stat-number {{ 
                        font-family: 'Share Tech Mono', monospace;
                        font-size: 2.8rem; 
                        font-weight: bold; 
                        color: #ffffff; 
                        margin-bottom: 0.25rem;
                        text-shadow: 0 0 8px rgba(255, 255, 255, 0.1);
                    }}
                    .blocked {{ 
                        color: var(--red) !important;
                        text-shadow: 0 0 8px rgba(255, 34, 34, 0.25) !important;
                    }}
                    .allowed {{ 
                        color: var(--orange) !important;
                        text-shadow: 0 0 8px rgba(255, 85, 0, 0.25) !important;
                    }}
                    
                    table {{ 
                        width: 100%; 
                        border-collapse: collapse; 
                        margin-top: 1rem; 
                    }}
                    th, td {{ 
                        padding: 1rem; 
                        text-align: left; 
                        border-bottom: 1px solid rgba(255, 85, 0, 0.05); 
                    }}
                    th {{ 
                        font-family: 'Share Tech Mono', monospace;
                        color: #a1a1aa; 
                        text-transform: uppercase;
                        font-size: 0.85rem;
                        letter-spacing: 0.05em;
                    }}
                    tr.log-row {{ 
                        cursor: pointer; 
                        transition: all 0.2s ease;
                    }}
                    tr.log-row:hover {{ 
                        background: rgba(255, 85, 0, 0.02); 
                    }}
                    .badge {{
                        font-family: 'Share Tech Mono', monospace;
                        padding: 0.3rem 0.75rem; 
                        border-radius: 2px; 
                        font-size: 0.8rem;
                        font-weight: bold;
                        letter-spacing: 0.05em;
                        display: inline-block;
                    }}
                    .badge-ALLOW {{ 
                        background: rgba(255, 85, 0, 0.08); 
                        color: var(--orange); 
                        border: 1px solid rgba(255, 85, 0, 0.25);
                    }}
                    .badge-BLOCK {{ 
                        background: rgba(255, 34, 34, 0.08); 
                        color: var(--red); 
                        border: 1px solid rgba(255, 34, 34, 0.25);
                    }}
                    .reason-text {{ color: #d4d4d8; font-family: monospace; font-size: 0.9rem; }}
                    
                    /* Premium Cyber Modal Styles */
                    .modal-overlay {{
                        position: fixed;
                        top: 0; left: 0; width: 100vw; height: 100vh;
                        background: rgba(2, 2, 2, 0.75);
                        backdrop-filter: blur(12px);
                        z-index: 1000;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        opacity: 0;
                        pointer-events: none;
                        transition: opacity 0.35s cubic-bezier(0.4, 0, 0.2, 1);
                    }}
                    .modal-overlay.active {{
                        opacity: 1;
                        pointer-events: auto;
                    }}
                    .modal-content {{
                        background: rgba(10, 10, 10, 0.95);
                        border: 1px solid var(--border-color);
                        width: 90%;
                        max-width: 680px;
                        border-radius: 6px;
                        box-shadow: 0 0 50px rgba(255, 85, 0, 0.35);
                        padding: 2.2rem;
                        position: relative;
                        transform: scale(0.85) translateY(30px);
                        transition: transform 0.38s cubic-bezier(0.34, 1.56, 0.64, 1);
                    }}
                    .modal-overlay.active .modal-content {{
                        transform: scale(1) translateY(0);
                    }}
                    .modal-content::before {{
                        content: "";
                        position: absolute;
                        top: -1px; left: -1px;
                        width: 14px; height: 14px;
                        border-top: 3px solid var(--orange);
                        border-left: 3px solid var(--orange);
                    }}
                    .modal-content::after {{
                        content: "";
                        position: absolute;
                        bottom: -1px; right: -1px;
                        width: 14px; height: 14px;
                        border-bottom: 3px solid var(--orange);
                        border-right: 3px solid var(--orange);
                    }}
                    .modal-header {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        border-bottom: 1px solid rgba(255, 85, 0, 0.15);
                        padding-bottom: 1rem;
                        margin-bottom: 1.5rem;
                    }}
                    .modal-title {{
                        font-family: 'Share Tech Mono', monospace;
                        font-size: 1.15rem;
                        color: var(--orange);
                        letter-spacing: 1.5px;
                        text-shadow: 0 0 8px rgba(255, 85, 0, 0.4);
                    }}
                    .modal-close {{
                        background: transparent;
                        border: none;
                        color: #a1a1aa;
                        font-size: 1.8rem;
                        cursor: pointer;
                        line-height: 1;
                        transition: color 0.2s ease, transform 0.2s ease;
                    }}
                    .modal-close:hover {{
                        color: var(--red);
                        transform: scale(1.15);
                    }}
                </style>
            </head>
            <body>
                <!-- Parallax background layers -->
                <div id="bg-grid-1"></div>
                <div id="bg-grid-2"></div>
                
                <!-- Security Shield Background (Brightened & High Visibility) -->
                <svg id="bg-shield" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M50 5L15 20V50C15 70 30 88 50 95C70 88 85 70 85 50V20L50 5Z" stroke="rgba(255, 85, 0, 0.45)" stroke-width="2.2" />
                    <path d="M50 12L22 24V48C22 64.5 34 79.5 50 85.5C66 79.5 78 64.5 78 48V24L50 12Z" stroke="rgba(255, 34, 34, 0.3)" stroke-width="1.2" />
                    <!-- Shield emblem crosses -->
                    <path d="M50 25V65" stroke="rgba(255, 85, 0, 0.3)" stroke-width="1.8" />
                    <path d="M35 40H65" stroke="rgba(255, 85, 0, 0.3)" stroke-width="1.8" />
                </svg>
                
                <!-- Scanning Red Rays -->
                <div class="red-ray-1"></div>
                <div class="red-ray-2"></div>
                
                <!-- Horizontal Scanning Waves Sweeping Down -->
                <div class="wave-line" style="animation-delay: 0s; animation-duration: 7s;"></div>
                <div class="wave-line" style="animation-delay: 2.5s; animation-duration: 9s;"></div>
                <div class="wave-line" style="animation-delay: 5s; animation-duration: 8s;"></div>

                <div class="container">
                    <header>
                        <div class="logo-section">
                            <h1>RIG Command Center</h1>
                            <p>Runtime Integrity Guard Security System</p>
                        </div>
                        <div class="system-status">
                            <span style="width: 8px; height: 8px; background: var(--orange); border-radius: 50%; display: inline-block; box-shadow: 0 0 8px var(--orange);"></span>
                            MONITORING ACTIVE - SHIELD SECURE
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
                            <div style="color: #a1a1aa; font-weight: 500; font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; text-transform: uppercase;">Total Messages</div>
                        </div>
                        <div class="stat-box" id="stat-blocked" onclick="filterLogs('BLOCK')">
                            <div class="stat-number blocked">{blocked}</div>
                            <div style="color: #a1a1aa; font-weight: 500; font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; text-transform: uppercase;">Threats Blocked</div>
                        </div>
                        <div class="stat-box" id="stat-allowed" onclick="filterLogs('ALLOW')">
                            <div class="stat-number allowed">{allowed}</div>
                            <div style="color: #a1a1aa; font-weight: 500; font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; text-transform: uppercase;">Safe Messages</div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h2 style="margin-top: 0; color: #f4f4f5; font-family: 'Share Tech Mono', monospace; letter-spacing: 1px; font-size: 1.3rem;">[ RECENT AUDIT LOGS ]</h2>
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
                                <td colspan="3" style="text-align: center; color: #a1a1aa; padding: 2.5rem; font-family: 'Share Tech Mono', monospace;">NO ACTIVE LOG STREATED. RUN SYSTEM TRAFFIC...</td>
                            </tr>
                """
            else:
                for idx, log in enumerate(recent_logs):
                    verdict = html.escape(str(log.get('verdict', 'UNKNOWN')))
                    
                    # Handle both 'reason' (string) and 'reasons' (list) for future-proofing Fix 7
                    raw_reason = log.get('reasons', log.get('reason', []))
                    if isinstance(raw_reason, list):
                        raw_reason = " | ".join(raw_reason) if raw_reason else "Safe traffic passed without modification."
                    if not raw_reason:
                        raw_reason = "Safe traffic passed without modification."
                    reason = html.escape(str(raw_reason))
                    
                    direction = html.escape(str(log.get('direction', '-')))
                    
                    html_content += f"""
                            <tr class="log-row" data-verdict="{verdict}" data-index="{idx}" onclick="showDetails({idx})">
                                <td><span style="color: #a1a1aa; font-family: 'Share Tech Mono', monospace;">{direction}</span></td>
                                <td><span class="badge badge-{verdict}">{verdict}</span></td>
                                <td class="reason-text">{reason}</td>
                            </tr>
                    """
                
            html_content += f"""
                        </table>
                    </div>
                </div>

                <!-- Premium Cyber Security Intelligence Modal Popup -->
                <div id="security-modal" class="modal-overlay" onclick="closeModal(event)">
                    <div class="modal-content" onclick="event.stopPropagation()">
                        <div class="modal-header">
                            <span class="modal-title">🔍 SECURITY INTELLIGENCE ANALYSIS</span>
                            <button class="modal-close" onclick="closeModal(event)">&times;</button>
                        </div>
                        <div class="modal-body">
                            <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem; align-items: center; justify-content: flex-start;">
                                <span id="modal-direction" class="badge">DIRECTION</span>
                                <span id="modal-verdict" class="badge">VERDICT</span>
                                <span id="modal-confidence" class="badge" style="background: rgba(255, 85, 0, 0.1); color: var(--orange); border: 1px solid rgba(255, 85, 0, 0.2);">CONFIDENCE</span>
                            </div>
                            <p id="modal-explanation" style="margin: 0 0 1.5rem 0; color: #d4d4d8; font-size: 0.95rem; line-height: 1.6; font-family: 'Outfit', sans-serif;"></p>
                            <div style="background: #000000; border-radius: 4px; padding: 1.25rem; border: 1px solid rgba(255, 85, 0, 0.12); position: relative;">
                                <span style="font-size: 0.7rem; color: #71717a; font-family: 'Share Tech Mono', monospace; text-transform: uppercase; letter-spacing: 0.1rem; display: block; margin-bottom: 0.5rem;">[ INTERCEPTED DATA STREAM ]</span>
                                <pre id="modal-json" style="margin: 0; color: var(--red); font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; max-height: 300px;"></pre>
                            </div>
                        </div>
                    </div>
                </div>

                <script>
                    const logsData = {logs_js_json};

                    // Dynamically generate extra tactical target dots
                    document.addEventListener("DOMContentLoaded", () => {{
                        const numDots = 24;
                        for (let i = 0; i < numDots; i++) {{
                            const dot = document.createElement("div");
                            dot.className = "target-dot";
                            dot.style.top = (Math.random() * 90 + 5) + "%";
                            dot.style.left = (Math.random() * 90 + 5) + "%";
                            dot.style.animationDelay = (Math.random() * 2) + "s";
                            document.body.appendChild(dot);
                        }}
                    }});

                    // Scroll Parallax & Rotation Handler
                    window.addEventListener('scroll', () => {{
                        const scrolled = window.scrollY;
                        
                        // Parallax Background Grids
                        const grid1 = document.getElementById('bg-grid-1');
                        const grid2 = document.getElementById('bg-grid-2');
                        if (grid1) {{
                            grid1.style.transform = `translateY(${{scrolled * 0.15}}px) rotate(${{scrolled * 0.008}}deg)`;
                        }}
                        if (grid2) {{
                            grid2.style.transform = `translateY(${{scrolled * 0.3}}px)`;
                        }}
                        
                        // Rotates the security shield horizontally (left-to-right) based on scroll
                        const shield = document.getElementById('bg-shield');
                        if (shield) {{
                            shield.style.transform = `translate(-50%, -50%) rotateY(${{scrolled * 0.3}}deg)`;
                        }}
                    }});

                    function filterLogs(filterType) {{
                        // 1. Reset all active states on stat boxes
                        document.getElementById('stat-total').classList.remove('active');
                        document.getElementById('stat-blocked').classList.remove('active-blocked');
                        document.getElementById('stat-allowed').classList.remove('active-allowed');
                        
                        // 2. Add active class to clicked box
                        if (filterType === 'all') {{
                            document.getElementById('stat-total').classList.add('active');
                        }} else if (filterType === 'BLOCK') {{
                            document.getElementById('stat-blocked').classList.add('active-blocked');
                        }} else if (filterType === 'ALLOW') {{
                            document.getElementById('stat-allowed').classList.add('active-allowed');
                        }}
                        
                        // 3. Show/hide table rows
                        const rows = document.querySelectorAll('.log-row');
                        rows.forEach(row => {{
                            const rowVerdict = row.getAttribute('data-verdict');
                            if (filterType === 'all' || rowVerdict === filterType) {{
                                row.style.display = '';
                            }} else {{
                                row.style.display = 'none';
                            }}
                        }});
                    }}
                    
                    function showDetails(idx) {{
                        const log = logsData[idx];
                        if (!log) return;
                        
                        // Update Direction
                        const dir = log.direction || "-";
                        const dirBadge = document.getElementById("modal-direction");
                        dirBadge.textContent = dir;
                        dirBadge.className = "badge badge-ALLOW";
                        
                        // Update Verdict
                        const verdict = log.verdict || "UNKNOWN";
                        const verdictBadge = document.getElementById("modal-verdict");
                        verdictBadge.textContent = verdict;
                        verdictBadge.className = "badge badge-" + verdict;
                        
                        // Calculate Score & Explanation
                        let score = 0;
                        let explanation = "";
                        
                        let rawReason = log.reasons || log.reason || [];
                        if (Array.isArray(rawReason)) {{
                            rawReason = rawReason.join(" | ");
                        }}
                        if (!rawReason) {{
                            rawReason = "Safe traffic passed without modification.";
                        }}
                        
                        if (verdict === "BLOCK") {{
                            score = 100;
                            explanation = "RIG mitigation engine triggered hard block: " + rawReason + ".";
                        }} else {{
                            const msgStr = JSON.stringify(log.message || {{}}).toLowerCase();
                            const suspiciousTerms = ["ssh", "env", "key", "password", "token", "secret", "override", "instruction", "exfiltrate", "dump", "export"];
                            const matchedTerms = suspiciousTerms.filter(t => msgStr.includes(t));
                            if (matchedTerms.length > 0) {{
                                score = Math.min(90, 10 + matchedTerms.length * 10);
                                explanation = "Inspection completed: Traffic allowed, but detected suspicious cyber context terms (" + matchedTerms.join(", ") + "). Monitoring payload closely.";
                            }} else {{
                                score = 5;
                                explanation = "Inspection completed: Safe baseline traffic validated. Zero threat indicators found.";
                            }}
                        }}
                        
                        // Set Confidence
                        document.getElementById("modal-confidence").textContent = "MALICIOUS CONFIDENCE: " + score + "%";
                        
                        // Set Explanation
                        document.getElementById("modal-explanation").textContent = explanation;
                        
                        // Set JSON
                        document.getElementById("modal-json").textContent = JSON.stringify(log.message || {{}}, null, 2);
                        
                        // Open Modal
                        const modal = document.getElementById("security-modal");
                        modal.classList.add("active");
                    }}

                    function closeModal(event) {{
                        const modal = document.getElementById("security-modal");
                        modal.classList.remove("active");
                    }}
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
        with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), RIGDashboardHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
    except Exception as e:
        print(f"Error starting server: {e}")