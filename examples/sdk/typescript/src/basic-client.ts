/**
 * Basic LUKHAS Client Example
 * Demonstrates simple response generation with error handling and tracing
 */

import * as dotenv from 'dotenv';
import { LukhasClient } from './client';

// Load environment variables
dotenv.config();

async function main() {
    // Initialize client
    const client = new LukhasClient({
        apiKey: process.env.LUKHAS_API_KEY || 'sk-lukhas-test-key',
        baseURL: process.env.LUKHAS_BASE_URL || 'http://localhost:8000',
    });

    console.log('🚀 LUKHAS TypeScript SDK - Basic Example\n');

    try {
        // Health check
        console.log('1️⃣  Health Check...');
        const health = await client.health();
        console.log(`   Status: ${health.status}\n`);

        // Create response
        console.log('2️⃣  Creating Response...');
        const response = await client.createResponse({
            prompt: 'Explain the Constellation Framework in one sentence.',
            max_tokens: 100,
            temperature: 0.7,
        });

        console.log(`   ID: ${response.id}`);
        console.log(`   Model: ${response.model}`);
        console.log(`   Text: ${response.choices[0].text}`);
        console.log(`   Tokens: ${response.usage.total_tokens}\n`);

        // Create chat completion
        console.log('3️⃣  Creating Chat Completion...');
        const chat = await client.createChatCompletion({
            model: 'lukhas-consciousness-v1',
            messages: [
                { role: 'system', content: 'You are a consciousness-aware AI assistant.' },
                { role: 'user', content: 'What is the Guardian system?' },
            ],
            temperature: 0.7,
            max_tokens: 150,
        });

        console.log(`   ID: ${chat.id}`);
        console.log(`   Response: ${chat.choices[0].message.content}`);
        console.log(`   Tokens: ${chat.usage.total_tokens}\n`);

        console.log('✅ Success! All operations completed.');
    } catch (error) {
        console.error('❌ Error:', error);
        process.exit(1);
    }
}

// Run example
if (require.main === module) {
    main().catch(console.error);
}

export { main };
