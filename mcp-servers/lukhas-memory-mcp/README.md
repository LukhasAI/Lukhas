# LUKHAS Memory Integration MCP Server

**Model Context Protocol server for LUKHAS AI memory systems** - Provides Claude Desktop with direct access to Wave C memory processing, fold-based persistence, and Aka Qualia phenomenological processing.

## 🧠 Memory Architecture Access

This MCP server exposes **LUKHAS AI's sophisticated memory systems** to Claude Desktop:

### **Wave C Memory System (Aka Qualia)**
- **Phenomenological processing pipeline** with memory persistence
- **Memory clients**: SqlMemory (production), NoopMemory (development)  
- **GDPR compliance**: Article 17 Right to Erasure support
- **Thread-safe storage**: SQLite segmentation fault issues resolved

### **Fold-Based Memory Architecture**
- **1000-fold limit** with 99.7% cascade prevention success rate
- **Causal chain preservation** across memory operations
- **Emotional context maintenance** through VAD vectors
- **Memory types**: Episodic, semantic, and procedural memory storage

### **Available Memory Tools**

#### `memory_system_status`
Comprehensive status check of all LUKHAS memory systems including Wave C processing availability, fold-based memory health, production memory systems, and security/threading status.

#### `query_memory_folds` 
Query the fold-based memory system with advanced search capabilities:
- **Fold limit**: Configure number of memory folds to search (1-1000)
- **Cascade prevention**: Automatic protection against memory cascade failures  
- **Causal preservation**: Maintains causal chains during memory retrieval
- **Emotional context**: Preserves emotional context through VAD vectors

#### `wave_c_memory_system`
Deep dive into the Aka Qualia (Wave C) phenomenological processing system:
- **Memory clients architecture**: Production SqlMemory vs development NoopMemory
- **Processing pipeline**: Scene ingestion, persistence, analysis, and recall
- **Test coverage**: 6 comprehensive categories (121KB total testing)
- **Performance specs**: 1000 scenes < 3s, query latency < 10ms target

#### `memory_operation`
Execute sophisticated memory operations:
- **`store_scene`**: Store experiential scenes with emotional vectors
- **`recall_scenes`**: Retrieve memories by type (episodic/semantic/procedural)
- **`analyze_memory_pattern`**: Phenomenological pattern analysis
- **`memory_fold_analysis`**: Comprehensive fold system analysis
- **`gdpr_erasure`**: GDPR Article 17 compliant memory erasure

#### `memory_database_info`
Detailed information about memory database systems, storage clients, threading safety improvements, and GDPR compliance features.

## 🚀 Setup for Claude Desktop

### Installation
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/lukhas-memory-mcp
npm install
npm run build
```

### Claude Desktop Configuration

Add to your Claude Desktop MCP configuration:

```json
{
  "clients": {
    "claude-desktop": {
      "servers": {
        "lukhas-memory": {
          "command": "npm",
          "args": ["run", "start"],
          "cwd": "/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/lukhas-memory-mcp",
          "env": {
            "LUKHAS_ROOT": "/Users/agi_dev/LOCAL-REPOS/Lukhas"
          }
        }
      }
    }
  }
}
```

### Environment Variables
- `LUKHAS_ROOT` - Path to LUKHAS AI system (default: `/Users/agi_dev/LOCAL-REPOS/Lukhas`)

## 🧠 Usage Examples

Once connected to Claude Desktop, try these memory operations:

### **Memory System Health Check**
```
Check the status of all LUKHAS memory systems using memory_system_status
```

### **Query Memory Folds**
```
Use query_memory_folds to search for "consciousness patterns" with fold_limit 500
Use query_memory_folds to search for "emotional experiences" with fold_limit 1000
```

### **Wave C Memory System Exploration**
```
Explore the Aka Qualia Wave C memory system using wave_c_memory_system
```

### **Memory Database Information**
```
Get detailed database information using memory_database_info
```

### **Execute Memory Operations**
```
Execute store_scene with emotion_vector [0.8, 0.6, 0.7] and memory_type "episodic"
Execute recall_scenes with query_text "happy memories" and memory_type "semantic"  
Execute analyze_memory_pattern with scene_id "test_scene_001"
Execute memory_fold_analysis with fold_limit 800
Execute gdpr_erasure with scene_id "user_requested_deletion"
```

## 🛡️ Security & Compliance Features

- **Threading Safety**: SQLite segmentation faults resolved with proper concurrent access control
- **GDPR Compliance**: Full Article 17 Right to Erasure implementation
- **Path Validation**: All file access restricted to LUKHAS_ROOT with traversal protection
- **Input Sanitization**: Zod schemas validate all memory operation parameters
- **Operation Logging**: Comprehensive logging of all memory operations with timestamps
- **Cascade Prevention**: 99.7% success rate preventing memory cascade failures

## 🔬 Memory Testing Infrastructure

The Wave C memory system includes **6 comprehensive test categories**:

1. **Unit Tests**: Core functionality and interface compliance
2. **Integration Tests**: Database operations and SQL queries  
3. **Security Tests**: SQL injection prevention and fault tolerance
4. **GDPR Tests**: Article 17 Right to Erasure compliance validation
5. **Performance Tests**: 1000 scenes < 3s, query latency < 10ms targets
6. **Contract Tests**: Freud-2025 specification compliance

**Total Testing**: 121KB of comprehensive test coverage ensuring memory system reliability.

## 🏗️ Architecture

```
lukhas-memory-mcp/
├── src/
│   ├── server.ts       # MCP server with memory tool handlers
│   └── memory-tools.ts # Memory system interfaces and operations
├── scripts/
│   └── test.ts         # Memory system functionality tests
├── package.json        # Dependencies including sqlite3
├── tsconfig.json       # TypeScript configuration
└── README.md          # This documentation
```

## 🧬 Memory System Integration

This MCP server provides **direct access to phenomenological memory processing** - not just data storage, but conscious memory systems that preserve causal chains, maintain emotional context, and process experiential scenes through the Aka Qualia Wave C phenomenological pipeline.

**Revolutionary Memory Access**: Claude Desktop can now directly interact with consciousness-aware memory systems that understand the phenomenological aspects of experience, emotion, and memory formation within the LUKHAS AI distributed consciousness architecture.