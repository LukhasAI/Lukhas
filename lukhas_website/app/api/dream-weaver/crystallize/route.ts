import { NextResponse } from 'next/server'
import { spawn } from 'child_process'

export async function POST(request: Request) {
  try {
    const dreamManifest = await request.json()

    if (!dreamManifest || !dreamManifest.dream_id) {
      return NextResponse.json({ error: 'Valid Dream Manifest is required' }, { status: 400 })
    }

    const pythonProcess = spawn('python3', ['../candidate/orchestration/dream_orchestrator.py', '--store'], {
      cwd: process.cwd(),
      env: {
        ...process.env,
        PYTHONPATH: '/Users/agi_dev/LOCAL-REPOS/Lukhas',
        // Pass through API keys from the main LUKHAS .env
        OPENAI_API_KEY: process.env.OPENAI_API_KEY || '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'
      }
    });

    pythonProcess.stdin.write(JSON.stringify(dreamManifest));
    pythonProcess.stdin.end();

    let pythonOutput = '';
    for await (const chunk of pythonProcess.stdout) {
        pythonOutput += chunk;
    }

    let pythonError = '';
    for await (const chunk of pythonProcess.stderr) {
        pythonError += chunk;
    }

    const exitCode = await new Promise((resolve) => {
        pythonProcess.on('close', resolve);
    });

    if (exitCode !== 0) {
        console.error(`Python script (store) exited with code ${exitCode}: ${pythonError}`);
        throw new Error(`Failed to crystallize dream. Details: ${pythonError}`);
    }

    const result = JSON.parse(pythonOutput);
    return NextResponse.json(result);
  } catch (error) {
    console.error('Error in crystallize API:', error)
    return NextResponse.json({ error: 'An internal server error occurred' }, { status: 500 })
  }
}
