// adapters/modelRegistry.js
export const modelRegistry = {
    async promote({ modelId, gate, dryRun }) {
        // Real impl would call registry API; here we just echo input.
        return { modelId, gate, dryRun };
    }
};