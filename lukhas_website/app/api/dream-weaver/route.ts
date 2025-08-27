import { NextResponse } from 'next/server'
import { spawn } from 'child_process'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { text } = body

    if (!text) {
      return NextResponse.json({ error: 'Dream seed text is required' }, { status: 400 })
    }

    // Execute the python orchestrator script
    const pythonProcess = spawn('python3', ['candidate/orchestration/dream_orchestrator.py'], {
      cwd: process.cwd() // Ensure the script is run from the root directory
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

    // The python script should only output the JSON string to stdout
    const dreamManifest = JSON.parse(pythonOutput);
    return NextResponse.json(dreamManifest);
  } catch (error) {
    console.error('Error in dream-weaver API:', error)
    return NextResponse.json({ error: 'An internal server error occurred' }, { status: 500 })
  }
}
