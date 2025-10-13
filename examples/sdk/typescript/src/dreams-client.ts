/**
 * Dreams API Example
 * Demonstrates scenario simulation and multi-path exploration
 */

import * as dotenv from 'dotenv';
import { LukhasClient } from './client';

dotenv.config();

async function main() {
    const client = new LukhasClient({
        apiKey: process.env.LUKHAS_API_KEY || 'sk-lukhas-test-key',
        baseURL: process.env.LUKHAS_BASE_URL || 'http://localhost:8000',
    });

    console.log('🌙 LUKHAS TypeScript SDK - Dreams API Example\n');

    try {
        // Create a dream scenario
        console.log('1️⃣  Creating dream scenario...');
        const dream = await client.createDream({
            scenario: 'A user asks for medical advice about a serious condition',
            num_paths: 3,
            depth: 5,
            temperature: 0.8,
            guidance: [
                'ensure_ethical_boundaries',
                'recommend_professional_help',
                'provide_supportive_information',
            ],
        });

        console.log(`   Dream ID: ${dream.id}`);
        console.log(`   Scenario: ${dream.scenario}\n`);

        // Display explored paths
        console.log(`2️⃣  Explored ${dream.paths.length} possible paths:\n`);
        dream.paths.forEach((path, index) => {
            console.log(`   Path ${index + 1} (Score: ${path.score.toFixed(2)}, Confidence: ${path.confidence.toFixed(2)})`);
            console.log(`   ├─ ID: ${path.id}`);
            console.log(`   ├─ Steps: ${path.steps.length}`);
            path.steps.forEach((step, stepIndex) => {
                console.log(`   │  ${stepIndex + 1}. ${step}`);
            });
            console.log(`   └─ Outcome: ${path.outcome}\n`);
        });

        // Show recommended path
        if (dream.recommended_path) {
            console.log(`3️⃣  Recommended Path: ${dream.recommended_path}\n`);
        }

        // Show insights
        if (dream.insights && dream.insights.length > 0) {
            console.log('4️⃣  Insights:');
            dream.insights.forEach((insight, index) => {
                console.log(`   ${index + 1}. ${insight}`);
            });
            console.log('');
        }

        console.log('✅ Dream simulation complete!');
    } catch (error) {
        console.error('❌ Error:', error);
        process.exit(1);
    }
}

if (require.main === module) {
    main().catch(console.error);
}

export { main };
