import { NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'

export async function GET() {
  // The Python script is located at `lukhas_website/scripts/get_audit_log.py`
  // The Next.js server runs from the `lukhas_website` directory root.
  // So the path to the script is relative from there.
  const scriptPath = path.join(process.cwd(), 'scripts', 'get_audit_log.py')
  const pythonProcess = spawn('python3', [scriptPath])

  let data = ''
  for await (const chunk of pythonProcess.stdout) {
    data += chunk.toString()
  }

  let error = ''
  for await (const chunk of pythonProcess.stderr) {
    error += chunk.toString()
  }

  const exitCode = await new Promise((resolve) => {
    pythonProcess.on('close', resolve)
  })

  if (exitCode) {
    console.error(`Python script error: ${error}`)
    return NextResponse.json(
      {
        error: 'Failed to fetch audit log',
        details: error,
      },
      { status: 500 }
    )
  }

  try {
    const auditLog = JSON.parse(data)
    return NextResponse.json(auditLog)
  } catch (e) {
    console.error(`JSON parse error: ${e}`)
    return NextResponse.json(
      {
        error: 'Failed to parse audit log data',
        details: data, // send back the raw data for debugging
      },
      { status: 500 }
    )
  }
}
