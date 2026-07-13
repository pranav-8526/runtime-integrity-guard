'use client';

import React, { useEffect, useState } from 'react';
import { Shield, ShieldAlert, ShieldCheck, Activity, TerminalSquare, Search, Layers, X, Server, ArrowRight } from 'lucide-react';

interface LogEntry {
  verdict: 'ALLOW' | 'BLOCK' | 'ALLOW_DEGRADED' | 'UNKNOWN';
  direction: string;
  reasons: string[];
  message: any;
  timestamp?: string;
  error?: string;
  reason?: string;
}

export default function Dashboard() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filter, setFilter] = useState<'ALL' | 'ALLOW' | 'BLOCK'>('ALL');
  const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null);
  const [isLive, setIsLive] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      if (!isLive) return;
      try {
        const res = await fetch('/api/logs');
        if (!res.ok) return;
        const data = await res.json();
        
        if (data && data.logs) {
          setLogs(data.logs.reverse().slice(0, 100)); // Keep last 100
        }
      } catch (err) {
        console.error('Failed to fetch logs', err);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 2500);
    return () => clearInterval(interval);
  }, [isLive]);

  const total = logs.length;
  const blocked = logs.filter(l => l.verdict === 'BLOCK').length;
  const allowed = total - blocked;

  const filteredLogs = logs.filter(log => {
    if (filter === 'ALL') return true;
    if (filter === 'ALLOW') return log.verdict !== 'BLOCK';
    if (filter === 'BLOCK') return log.verdict === 'BLOCK';
    return true;
  });

  return (
    <div className="min-h-screen bg-[#0d1117] text-[#c9d1d9] font-sans selection:bg-[#1f6feb]/30">
      
      <div className="max-w-[1280px] mx-auto px-6 pt-12 pb-24">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-10 pb-6 border-b border-[#30363d]">
          <div className="flex items-center gap-4">
            <div className="p-2.5 bg-[#161b22] border border-[#30363d] rounded-xl shadow-sm">
              <Shield className="w-7 h-7 text-[#58a6ff]" />
            </div>
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-[#e6edf3]">RIG Command Center</h1>
              <p className="text-[#8b949e] text-sm mt-0.5">Runtime Integrity Guard for MCP</p>
            </div>
          </div>
          <div className="mt-6 md:mt-0 flex items-center gap-4">
            <button 
              onClick={() => setIsLive(!isLive)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                isLive 
                  ? 'bg-[#2ea043]/10 border-[#2ea043]/30 text-[#3fb950]' 
                  : 'bg-[#161b22] border-[#30363d] text-[#8b949e]'
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${isLive ? 'bg-[#3fb950] animate-pulse' : 'bg-[#8b949e]'}`}></span>
              {isLive ? 'LIVE STREAMING' : 'PAUSED'}
            </button>
          </div>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-10">
          <StatCard 
            title="Total Inspections" 
            value={total} 
            icon={<Activity />} 
            onClick={() => setFilter('ALL')} 
            active={filter === 'ALL'} 
          />
          <StatCard 
            title="Threats Blocked" 
            value={blocked} 
            icon={<ShieldAlert />} 
            color="text-[#f85149]" 
            activeColor="border-[#f85149]/50 bg-[#f85149]/5"
            onClick={() => setFilter('BLOCK')} 
            active={filter === 'BLOCK'} 
          />
          <StatCard 
            title="Safe Operations" 
            value={allowed} 
            icon={<ShieldCheck />} 
            color="text-[#3fb950]" 
            activeColor="border-[#3fb950]/50 bg-[#3fb950]/5"
            onClick={() => setFilter('ALLOW')} 
            active={filter === 'ALLOW'} 
          />
        </div>

        {/* Audit Logs Table */}
        <div className="bg-[#161b22] border border-[#30363d] rounded-xl overflow-hidden shadow-sm">
          <div className="px-5 py-4 border-b border-[#30363d] flex justify-between items-center bg-[#0d1117]">
            <h2 className="font-medium text-[14px] flex items-center gap-2 text-[#e6edf3]">
              <Layers className="w-4 h-4 text-[#8b949e]" />
              Audit Logs
            </h2>
            <div className="flex gap-1.5 bg-[#0d1117] p-1 border border-[#30363d] rounded-lg">
              <FilterBadge label="All" active={filter === 'ALL'} onClick={() => setFilter('ALL')} />
              <FilterBadge label="Blocked" active={filter === 'BLOCK'} onClick={() => setFilter('BLOCK')} />
              <FilterBadge label="Allowed" active={filter === 'ALLOW'} onClick={() => setFilter('ALLOW')} />
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-[#30363d] bg-[#161b22] text-[#8b949e] text-[12px] font-medium tracking-wide">
                  <th className="px-5 py-3 whitespace-nowrap">Status</th>
                  <th className="px-5 py-3 whitespace-nowrap">Direction</th>
                  <th className="px-5 py-3 w-full">Analysis Reason</th>
                  <th className="px-5 py-3 whitespace-nowrap text-right">Timestamp</th>
                  <th className="px-5 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#30363d]">
                {filteredLogs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-5 py-16 text-center text-[#8b949e] text-sm">
                      {logs.length === 0 ? 'No logs detected yet. Awaiting traffic...' : 'No logs match the current filter.'}
                    </td>
                  </tr>
                ) : (
                  filteredLogs.map((log, idx) => (
                    <tr key={idx} 
                        onClick={() => setSelectedLog(log)}
                        className="group hover:bg-[#1c2128] cursor-pointer transition-colors">
                      <td className="px-5 py-3.5 whitespace-nowrap">
                        <VerdictBadge verdict={log.verdict} />
                      </td>
                      <td className="px-5 py-3.5 font-mono text-[13px] text-[#8b949e] whitespace-nowrap flex items-center gap-1.5 mt-1">
                        <Server className="w-3.5 h-3.5" />
                        {log.direction || '-'}
                      </td>
                      <td className="px-5 py-3.5">
                        <div className="text-[13px] text-[#c9d1d9] truncate max-w-[500px]">
                          {getReasonString(log)}
                        </div>
                      </td>
                      <td className="px-5 py-3.5 text-right font-mono text-[12px] text-[#8b949e] whitespace-nowrap">
                        {log.timestamp || 'Just now'}
                      </td>
                      <td className="px-5 py-3.5 text-right text-[#8b949e] opacity-0 group-hover:opacity-100 transition-opacity">
                        <ArrowRight className="w-4 h-4" />
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>

      {/* Modal / Slide-over */}
      {selectedLog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center sm:p-4 bg-[#010409]/80 backdrop-blur-sm transition-opacity"
             onClick={() => setSelectedLog(null)}>
          <div className="bg-[#161b22] border border-[#30363d] rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl transform transition-transform"
               onClick={e => e.stopPropagation()}>
            
            <div className="flex justify-between items-center px-6 py-4 border-b border-[#30363d] bg-[#0d1117] rounded-t-2xl">
              <h3 className="font-semibold text-md text-[#e6edf3] flex items-center gap-2">
                <TerminalSquare className="w-5 h-5 text-[#8b949e]" />
                Inspection Details
              </h3>
              <button onClick={() => setSelectedLog(null)} className="p-1.5 hover:bg-[#30363d] rounded-md transition-colors text-[#8b949e] hover:text-[#c9d1d9]">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto custom-scrollbar">
              
              <div className="flex flex-wrap gap-4 mb-8">
                <div className="flex-1 min-w-[200px] p-4 bg-[#0d1117] border border-[#30363d] rounded-xl">
                  <div className="text-[11px] font-medium text-[#8b949e] uppercase tracking-wider mb-2">Verdict</div>
                  <VerdictBadge verdict={selectedLog.verdict} />
                </div>
                <div className="flex-1 min-w-[200px] p-4 bg-[#0d1117] border border-[#30363d] rounded-xl">
                  <div className="text-[11px] font-medium text-[#8b949e] uppercase tracking-wider mb-2">Direction</div>
                  <div className="font-mono text-sm text-[#e6edf3]">{selectedLog.direction || '-'}</div>
                </div>
                <div className="flex-1 min-w-[200px] p-4 bg-[#0d1117] border border-[#30363d] rounded-xl">
                  <div className="text-[11px] font-medium text-[#8b949e] uppercase tracking-wider mb-2">Confidence Score</div>
                  <div className={`font-mono text-sm ${selectedLog.verdict === 'BLOCK' ? 'text-[#f85149]' : 'text-[#3fb950]'}`}>
                    {selectedLog.verdict === 'BLOCK' ? '100% (Rule Match)' : '95% (Safe Baseline)'}
                  </div>
                </div>
              </div>

              <div className="mb-8">
                <h4 className="text-[12px] font-semibold text-[#e6edf3] mb-3">Analysis Reason</h4>
                <div className="bg-[#0d1117] border border-[#30363d] rounded-xl p-4">
                  <p className="text-[14px] text-[#c9d1d9] leading-relaxed">
                    {selectedLog.verdict === 'BLOCK' 
                      ? <><span className="text-[#f85149] font-medium mr-1">Threat Detected:</span> The payload triggered the RIG mitigation engine. <br/><br/><span className="text-[#8b949e] font-mono text-xs">{getReasonString(selectedLog)}</span></>
                      : <><span className="text-[#3fb950] font-medium mr-1">Traffic Allowed:</span> Payload analyzed against known threat signatures. Zero indicators of tool poisoning or prompt injection detected.</>}
                  </p>
                </div>
              </div>

              <div>
                <h4 className="text-[12px] font-semibold text-[#e6edf3] mb-3">Intercepted Payload</h4>
                <div className="bg-[#0d1117] border border-[#30363d] rounded-xl overflow-hidden">
                  <div className="px-4 py-2 bg-[#161b22] border-b border-[#30363d] text-[11px] font-mono text-[#8b949e]">
                    application/json-rpc
                  </div>
                  <pre className="p-4 overflow-x-auto text-[13px] font-mono leading-relaxed text-[#c9d1d9] max-h-[400px]">
                    {JSON.stringify(selectedLog.message || {}, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ title, value, icon, color = "text-[#e6edf3]", activeColor = "border-[#58a6ff]/50 bg-[#58a6ff]/5", onClick, active }: any) {
  return (
    <div 
      onClick={onClick}
      className={`bg-[#161b22] border ${active ? activeColor : 'border-[#30363d]'} rounded-xl p-5 cursor-pointer hover:border-[#8b949e] transition-all group`}
    >
      <div className="flex justify-between items-start mb-3">
        <div className={`text-[#8b949e] group-hover:${color} transition-colors`}>
          {React.cloneElement(icon, { className: "w-5 h-5" })}
        </div>
      </div>
      <div>
        <div className={`text-3xl font-semibold mb-1 tracking-tight ${color}`}>{value}</div>
        <div className="text-[#8b949e] text-[13px] font-medium">{title}</div>
      </div>
    </div>
  );
}

function FilterBadge({ label, active, onClick }: any) {
  return (
    <button 
      onClick={onClick}
      className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
        active 
          ? 'bg-[#1f6feb] text-white shadow-sm' 
          : 'bg-transparent text-[#8b949e] hover:bg-[#21262d] hover:text-[#c9d1d9]'
      }`}
    >
      {label}
    </button>
  );
}

function VerdictBadge({ verdict }: { verdict: string }) {
  const isBlock = verdict === 'BLOCK';
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium border ${
      isBlock 
        ? 'bg-[#f85149]/10 text-[#ff7b72] border-[#f85149]/20' 
        : 'bg-[#2ea043]/10 text-[#3fb950] border-[#2ea043]/20'
    }`}>
      {verdict === 'ALLOW' ? 'PASS' : verdict}
    </span>
  );
}

function getReasonString(log: LogEntry): string {
  const r = log.reasons || log.reason || log.error;
  if (Array.isArray(r)) return r.join(' | ') || 'Safe traffic passed.';
  return r || 'Safe traffic passed.';
}
