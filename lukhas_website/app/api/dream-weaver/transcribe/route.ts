import { NextResponse } from 'next/server'
import OpenAI from 'openai'
import fs from 'fs'
import os from 'os'
import path from 'path'

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const audioBlob = formData.get('audio') as Blob;

    if (!audioBlob) {
      return NextResponse.json({ error: 'Audio blob is required' }, { status: 400 });
    }

    // Whisper API expects a file, so we need to save the blob to a temporary file
    const buffer = Buffer.from(await audioBlob.arrayBuffer());
    const tempFilePath = path.join(os.tmpdir(), `audio-${Date.now()}.webm`);
    fs.writeFileSync(tempFilePath, buffer);

    const transcription = await openai.audio.transcriptions.create({
      file: fs.createReadStream(tempFilePath),
      model: 'whisper-1',
    });

    // Clean up the temporary file
    fs.unlinkSync(tempFilePath);

    return NextResponse.json({ transcription: transcription.text });
  } catch (error) {
    console.error('Error in transcribe API:', error);
    const errorMessage = error instanceof Error ? error.message : 'An internal server error occurred';
    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}
