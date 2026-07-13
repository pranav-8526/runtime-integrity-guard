import { NextResponse } from 'next/server';
import * as fs from 'fs';
import * as path from 'path';

export async function GET() {
  try {
    // Navigate up from frontend directory to find the audit.jsonl in the root workspace
    // If running in Docker, it might be in /workspace, otherwise look in parent directory.
    const auditFilePath = process.env.AUDIT_LOG_PATH 
      ? process.env.AUDIT_LOG_PATH 
      : path.join(process.cwd(), '..', 'audit.jsonl');
    
    if (!fs.existsSync(auditFilePath)) {
      return NextResponse.json({ logs: [] });
    }

    const fileContent = fs.readFileSync(auditFilePath, 'utf-8');
    const lines = fileContent.split('\n');
    
    const logs = [];
    for (const line of lines) {
      if (line.trim()) {
        try {
          logs.push(JSON.parse(line));
        } catch (e) {
          // ignore parsing errors for partial lines
        }
      }
    }

    return NextResponse.json({ logs });
  } catch (error) {
    console.error('Error reading logs:', error);
    return NextResponse.json({ error: 'Failed to read logs' }, { status: 500 });
  }
}
