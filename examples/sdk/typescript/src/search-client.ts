/**
 * Search Index Example
 * Demonstrates vector search with semantic similarity
 */

import * as dotenv from 'dotenv';
import { LukhasClient } from './client';

dotenv.config();

async function main() {
    const client = new LukhasClient({
        apiKey: process.env.LUKHAS_API_KEY || 'sk-lukhas-test-key',
        baseURL: process.env.LUKHAS_BASE_URL || 'http://localhost:8000',
    });

    console.log('🔍 LUKHAS TypeScript SDK - Search Index Example\n');

    try {
        // Search for similar content
        console.log('1️⃣  Searching index...');
        const searchResults = await client.searchIndex({
            query: 'consciousness patterns in AI',
            index_name: 'consciousness-docs',
            top_k: 5,
            threshold: 0.7,
            filter: {
                category: 'technical',
            },
        });

        console.log(`   Found ${searchResults.total} results\n`);

        // Display results
        searchResults.results.forEach((result, index) => {
            console.log(`   ${index + 1}. Score: ${result.score.toFixed(4)}`);
            console.log(`      ID: ${result.id}`);
            if (result.content) {
                const preview = result.content.substring(0, 100);
                console.log(`      Preview: ${preview}...`);
            }
            if (result.metadata) {
                console.log(`      Metadata:`, JSON.stringify(result.metadata, null, 2));
            }
            console.log('');
        });

        console.log('✅ Search complete!');
    } catch (error) {
        console.error('❌ Error:', error);
        process.exit(1);
    }
}

if (require.main === module) {
    main().catch(console.error);
}

export { main };
