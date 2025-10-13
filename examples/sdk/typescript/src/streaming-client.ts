/**
 * Streaming SSE Example
 * Demonstrates real-time token streaming with Server-Sent Events
 */

import * as dotenv from 'dotenv';
import { LukhasClient, StreamChunk } from './client';

dotenv.config();

async function main() {
    const client = new LukhasClient({
        apiKey: process.env.LUKHAS_API_KEY || 'sk-lukhas-test-key',
        baseURL: process.env.LUKHAS_BASE_URL || 'http://localhost:8000',
    });

    console.log('🌊 LUKHAS TypeScript SDK - Streaming Example\n');
    console.log('Streaming response...\n');

    try {
        let fullText = '';
        let chunkCount = 0;

        await client.streamResponse(
            {
                prompt: 'Explain the MATRIZ cognitive engine in detail.',
                max_tokens: 300,
                temperature: 0.7,
                stream: true,
            },
            // onChunk callback
            (chunk: StreamChunk) => {
                chunkCount++;
                const text = chunk.choices[0].text || chunk.choices[0].delta?.content || '';
                if (text) {
                    process.stdout.write(text);
                    fullText += text;
                }
            },
            // onDone callback
            (traceId?: string) => {
                console.log('\n');
                console.log(`\n✅ Streaming complete!`);
                console.log(`   Chunks received: ${chunkCount}`);
                console.log(`   Total characters: ${fullText.length}`);
                if (traceId) {
                    console.log(`   Trace ID: ${traceId}`);
                }
            },
            // onError callback
            (error: Error) => {
                console.error(`\n❌ Stream error: ${error.message}`);
            }
        );
    } catch (error) {
        console.error('❌ Error:', error);
        process.exit(1);
    }
}

if (require.main === module) {
    main().catch(console.error);
}

export { main };
