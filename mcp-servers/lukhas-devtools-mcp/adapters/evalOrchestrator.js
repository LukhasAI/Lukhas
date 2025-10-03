// adapters/evalOrchestrator.js
// Swap this to your real orchestrator later; keep method signatures.
export const evalOrchestrator = {
    async run({ taskId, configId, dryRun }) {
        // Real impl could POST to orchestrator API and return jobId
        return { jobId: `job_${Math.random().toString(36).slice(2, 10)}`, dryRun };
    },
    async poll(jobId) {
        // Real impl would fetch status/result; stub returns null to let server drive sim
        return null;
    }
};