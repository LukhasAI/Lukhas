import { NextResponse } from 'next/server'
import { spawn } from 'child_process'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { text } = body

    if (!text) {
      return NextResponse.json({ error: 'Dream seed text is required' }, { status: 400 })
    }

    // Execute the python orchestrator script from the main LUKHAS repo
    const pythonProcess = spawn('python3', ['../candidate/orchestration/dream_orchestrator.py'], {
      cwd: process.cwd(), // Ensure the script is run from the root directory
      env: {
        ...process.env,
        PYTHONPATH: '/Users/agi_dev/LOCAL-REPOS/Lukhas',
        // Pass through API keys from the main LUKHAS .env
        OPENAI_API_KEY: process.env.OPENAI_API_KEY || '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'
      }
    });

    // Write the dream seed to the Python script's stdin
    pythonProcess.stdin.write(text);
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
        console.error(`Python script exited with code ${exitCode}: ${pythonError}`);
        throw new Error(`The dream orchestrator failed. Details: ${pythonError}`);
    }

    // Extract the JSON from the output (it's usually the last line)
    const outputLines = pythonOutput.trim().split('\n');
    const jsonLine = outputLines[outputLines.length - 1];
    
    try {
      const dreamManifest = JSON.parse(jsonLine);
      return NextResponse.json(dreamManifest);
    } catch (parseError) {
      console.error('Failed to parse JSON from output:', jsonLine);
      console.error('Full output:', pythonOutput);
      throw new Error(`Invalid JSON output from dream orchestrator: ${parseError}`);
    }
  } catch (error) {
    console.error('Error in dream-weaver API:', error)
    return NextResponse.json({ error: 'An internal server error occurred' }, { status: 500 })
  }
}
