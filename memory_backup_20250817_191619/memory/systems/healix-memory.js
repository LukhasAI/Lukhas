/**
 * Healix Memory System - JavaScript Implementation
 * DNA-inspired memory architecture for emotional and cultural memory mapping
 */

class MemoryStrand {
    static EMOTIONAL = 'emotional';
    static CULTURAL = 'cultural';
    static EXPERIENTIAL = 'experiential';
    static PROCEDURAL = 'procedural';
    static COGNITIVE = 'cognitive';
}

class MutationStrategy {
    static POINT = 'point';
    static INSERTION = 'insertion';
    static DELETION = 'deletion';
    static CROSSOVER = 'crossover';
}

// Emoji Archetype Mapping System
const ARCHETYPE_MAP = {
    "🦉": { archetype: "Sage", traits: ["Wisdom", "Insight"], vector: [0.8, -0.2, 0.5] },
    "🌊": { archetype: "Explorer", traits: ["Flow", "Curiosity"], vector: [0.4, 0.7, -0.3] },
    "🔮": { archetype: "Magician", traits: ["Transformation", "Vision"], vector: [0.9, 0.1, 0.8] },
    "🌌": { archetype: "Creator", traits: ["Innovation", "Imagination"], vector: [-0.5, 0.6, 0.4] },
    "🌸": { archetype: "Innocent", traits: ["Purity", "Wonder"], vector: [0.2, 0.8, 0.1] },
    "⚡": { archetype: "Hero", traits: ["Courage", "Action"], vector: [0.9, 0.3, -0.1] },
    "🌿": { archetype: "Caregiver", traits: ["Nurturing", "Growth"], vector: [0.1, 0.5, 0.9] },
    "🎭": { archetype: "Jester", traits: ["Joy", "Freedom"], vector: [-0.3, 0.9, 0.2] },
    "👑": { archetype: "Ruler", traits: ["Authority", "Order"], vector: [0.7, -0.4, 0.6] },
    "💀": { archetype: "Outlaw", traits: ["Rebellion", "Change"], vector: [-0.8, 0.2, -0.5] }
};

// Glymph wordbank for generating poetic backstories
const GLYMPH_WORDBANK = {
    sage: { nouns: ["Codex", "Lumen", "Scroll", "Oracle"], verbs: ["decrypts", "illuminates", "reveals", "whispers"] },
    explorer: { nouns: ["Horizon", "Current", "Path", "Compass"], verbs: ["navigates", "charts", "discovers", "ventures"] },
    magician: { nouns: ["Prism", "Catalyst", "Transmuter", "Weaver"], verbs: ["transforms", "manifests", "enchants", "channels"] },
    creator: { nouns: ["Canvas", "Forge", "Synthesis", "Genesis"], verbs: ["crafts", "births", "designs", "imagines"] },
    innocent: { nouns: ["Dawn", "Bloom", "Wonder", "Dream"], verbs: ["awakens", "blossoms", "hopes", "believes"] },
    hero: { nouns: ["Shield", "Quest", "Victory", "Champion"], verbs: ["defends", "conquers", "protects", "overcomes"] },
    caregiver: { nouns: ["Sanctuary", "Embrace", "Healing", "Garden"], verbs: ["nurtures", "shelters", "mends", "grows"] },
    jester: { nouns: ["Laughter", "Dance", "Freedom", "Spark"], verbs: ["delights", "celebrates", "liberates", "entertains"] },
    ruler: { nouns: ["Throne", "Decree", "Empire", "Crown"], verbs: ["commands", "governs", "ordains", "leads"] },
    outlaw: { nouns: ["Revolution", "Shadow", "Rebellion", "Phoenix"], verbs: ["defies", "disrupts", "challenges", "rises"] }
};

class HealixMapper {
    constructor() {
        this.strands = {
            [MemoryStrand.EMOTIONAL]: [],
            [MemoryStrand.CULTURAL]: [],
            [MemoryStrand.EXPERIENTIAL]: [],
            [MemoryStrand.PROCEDURAL]: [],
            [MemoryStrand.COGNITIVE]: []
        };

        // Helix properties
        this.quantumEncryption = true;
        this.mutationTracking = true;
        this.patternValidation = true;

        // Resonance settings
        this.resonanceThreshold = 0.75;
        this.patternCoherence = 0.9;

        // Current active memory
        this.activeMemory = null;
        this.currentArchetype = null;

        console.log("🧬 Healix Mapper initialized");
    }

    // Map emoji seed to archetype with composite vector
    mapEmojiArchetypes(emojiSeed) {
        const emojis = Array.from(emojiSeed).slice(0, 3);
        const components = emojis.map(emoji => ARCHETYPE_MAP[emoji] || ARCHETYPE_MAP["🌸"]);

        // Calculate composite vector
        const compositeVector = [0, 0, 0];
        components.forEach(comp => {
            compositeVector[0] += comp.vector[0];
            compositeVector[1] += comp.vector[1];
            compositeVector[2] += comp.vector[2];
        });

        // Normalize vector
        const magnitude = Math.sqrt(compositeVector[0]**2 + compositeVector[1]**2 + compositeVector[2]**2);
        if (magnitude > 0) {
            compositeVector[0] /= magnitude;
            compositeVector[1] /= magnitude;
            compositeVector[2] /= magnitude;
        }

        const primary = components.reduce((max, comp) =>
            comp.vector.reduce((a, b) => a + b) > max.vector.reduce((a, b) => a + b) ? comp : max
        );

        const shadow = components.reduce((min, comp) =>
            comp.vector.reduce((a, b) => a + b) < min.vector.reduce((a, b) => a + b) ? comp : min
        );

        return {
            primary,
            shadow,
            compositeVector,
            components,
            emojis
        };
    }

    // Generate poetic backstory for glymph
    generateGlymphBackstory(emojiSeed) {
        const archetypeData = this.mapEmojiArchetypes(emojiSeed);
        const primaryType = archetypeData.primary.archetype.toLowerCase();
        const wordbank = GLYMPH_WORDBANK[primaryType] || GLYMPH_WORDBANK.sage;

        const hashDigest = this.generateSimpleHash(emojiSeed);
        const noun = wordbank.nouns[Math.floor(Math.random() * wordbank.nouns.length)];
        const verb = wordbank.verbs[Math.floor(Math.random() * wordbank.verbs.length)];

        return {
            title: `${archetypeData.primary.archetype} of the ${noun}`,
            backstory: `Born of ${archetypeData.primary.traits[0]} and ${archetypeData.shadow.traits[1]}, this entity ${verb} the ${hashDigest.slice(10, 12)} realms.`,
            complianceTags: ["GDPR:pseudonymized", "EU_AI_Act:Art13"],
            hashDigest
        };
    }

    // Simple hash function for emoji seeds
    generateSimpleHash(input) {
        let hash = 0;
        for (let i = 0; i < input.length; i++) {
            const char = input.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return Math.abs(hash).toString(16);
    }

    // Calculate resonance based on vector magnitude and coherence
    calculateResonance(memory) {
        if (!memory.archetypeProfile) return 0.5;

        const vector = memory.archetypeProfile.compositeVector;
        const magnitude = Math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2);
        const coherence = memory.archetypeProfile.components.length > 0 ?
            Math.min(1.0, magnitude / memory.archetypeProfile.components.length) : 0.5;

        return Math.min(1.0, coherence * this.patternCoherence);
    }

    // Encode memory into helix structure
    async encodeMemory(memory, strandType, context = null) {
        if (this.patternValidation) {
            await this.validatePattern(memory, strandType);
        }

        // Process emoji seed for emotional/cultural strands
        if ((strandType === MemoryStrand.EMOTIONAL || strandType === MemoryStrand.CULTURAL) && memory.emojiSeed) {
            memory.archetypeProfile = this.mapEmojiArchetypes(memory.emojiSeed);
            memory.backstory = this.generateGlymphBackstory(memory.emojiSeed);
        }

        const memoryId = this.generateMemoryId(memory, strandType);
        const resonance = this.calculateResonance(memory);

        const encodedMemory = {
            id: memoryId,
            data: memory,
            created: new Date().toISOString(),
            mutations: [],
            resonance: resonance,
            context: context,
            strandType: strandType
        };

        this.strands[strandType].push(encodedMemory);
        this.activeMemory = encodedMemory;
        this.currentArchetype = memory.archetypeProfile;

        console.log(`🧬 Memory ${memoryId} encoded in ${strandType} strand with resonance ${resonance.toFixed(3)}`);
        return memoryId;
    }

    // Generate unique memory ID
    generateMemoryId(memory, strandType) {
        const timestamp = Date.now();
        const memoryHash = this.generateSimpleHash(JSON.stringify(memory));
        return `${strandType}_${memoryHash}_${timestamp}`;
    }

    // Validate memory pattern
    async validatePattern(memory, strandType) {
        // Basic validation rules
        if (!memory || typeof memory !== 'object') {
            throw new Error('Invalid memory object');
        }

        if (strandType === MemoryStrand.EMOTIONAL && !memory.emojiSeed) {
            console.warn('Emotional memory without emoji seed');
        }

        return true;
    }

    // Apply memory mutation
    async mutateMemory(memoryId, mutation, strategy) {
        const memory = this.findMemory(memoryId);
        if (!memory) return false;

        let success = false;

        switch (strategy) {
            case MutationStrategy.POINT:
                success = await this.applyPointMutation(memory, mutation);
                break;
            case MutationStrategy.INSERTION:
                success = await this.applyInsertion(memory, mutation);
                break;
            case MutationStrategy.DELETION:
                success = await this.applyDeletion(memory, mutation);
                break;
            case MutationStrategy.CROSSOVER:
                success = await this.applyCrossover(memory, mutation);
                break;
            default:
                throw new Error(`Unknown mutation strategy: ${strategy}`);
        }

        if (success) {
            memory.mutations.push({
                type: strategy,
                data: mutation,
                timestamp: new Date().toISOString()
            });

            // Recalculate resonance after mutation
            memory.resonance = this.calculateResonance(memory.data);
        }

        return success;
    }

    // Find memory by ID
    findMemory(memoryId) {
        for (const strand of Object.values(this.strands)) {
            const memory = strand.find(m => m.id === memoryId);
            if (memory) return memory;
        }
        return null;
    }

    // Get current archetype for visualization
    getCurrentArchetype() {
        return this.currentArchetype;
    }

    // Get active memory
    getActiveMemory() {
        return this.activeMemory;
    }

    // Get strand statistics
    getStrandStats() {
        const stats = {};
        for (const [strandType, memories] of Object.entries(this.strands)) {
            stats[strandType] = {
                count: memories.length,
                averageResonance: memories.length > 0 ?
                    memories.reduce((sum, m) => sum + m.resonance, 0) / memories.length : 0,
                totalMutations: memories.reduce((sum, m) => sum + m.mutations.length, 0)
            };
        }
        return stats;
    }

    // Simple mutation implementations
    async applyPointMutation(memory, mutation) {
        if (mutation.field && mutation.value) {
            memory.data[mutation.field] = mutation.value;
            return true;
        }
        return false;
    }

    async applyInsertion(memory, mutation) {
        if (mutation.field && mutation.value) {
            if (!memory.data[mutation.field]) {
                memory.data[mutation.field] = [];
            }
            if (Array.isArray(memory.data[mutation.field])) {
                memory.data[mutation.field].push(mutation.value);
                return true;
            }
        }
        return false;
    }

    async applyDeletion(memory, mutation) {
        if (mutation.field && memory.data[mutation.field]) {
            delete memory.data[mutation.field];
            return true;
        }
        return false;
    }

    async applyCrossover(memory, mutation) {
        if (mutation.sourceMemoryId) {
            const sourceMemory = this.findMemory(mutation.sourceMemoryId);
            if (sourceMemory && mutation.fields) {
                mutation.fields.forEach(field => {
                    if (sourceMemory.data[field]) {
                        memory.data[field] = sourceMemory.data[field];
                    }
                });
                return true;
            }
        }
        return false;
    }
}

// Export for use in other modules
window.HealixMapper = HealixMapper;
window.MemoryStrand = MemoryStrand;
window.MutationStrategy = MutationStrategy;
