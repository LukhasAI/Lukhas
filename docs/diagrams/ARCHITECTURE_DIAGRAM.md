# LUKHAS  Architecture Diagrams

## System Architecture Overview

```mermaid
graph TB
    subgraph "External Layer"
        U[Users] --> API[API Gateway]
        EXT[External Services] --> BR[Bridge Module]
    end
    
    subgraph "Guardian Layer"
        API --> GS[Guardian System]
        GS --> VAL[Validation]
        GS --> ETH[Ethics Engine]
        GS --> REM[Remediator]
    end
    
    subgraph "Orchestration Layer"
        VAL --> BH[Brain Hub]
        BH --> RT[Router]
        BH --> CONS[Consolidator]
        BH --> SCHED[Scheduler]
    end
    
    subgraph "Core Modules"
        RT --> CONSC[Consciousness]
        RT --> MEM[Memory]
        RT --> REAS[Reasoning]
        RT --> EMO[Emotion]
        RT --> DREAM[Dream Engine]
        RT --> QUANT[Quantum]
        RT --> BIO[Bio Systems]
    end
    
    subgraph "Infrastructure"
        MEM --> DB[(PostgreSQL)]
        MEM --> REDIS[(Redis)]
        CONSC --> REDIS
        BH --> MQ[Message Queue]
    end
    
    style GS fill:#ff6b6b,stroke:#c92a2a,stroke-width:4px
    style BH fill:#4dabf7,stroke:#1971c2,stroke-width:4px
    style MEM fill:#69db7c,stroke:#2f9e44,stroke-width:2px
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant User
    participant API as API Gateway
    participant Guardian
    participant Brain as Brain Hub
    participant Module as Module (Any)
    participant Memory
    participant Response
    
    User->>API: Request
    API->>Guardian: Validate Request
    Guardian-->>API: Approval/Rejection
    
    alt Request Approved
        API->>Brain: Forward Request
        Brain->>Brain: Generate GLYPH Token
        Brain->>Module: Dispatch GLYPH
        Module->>Module: Process
        Module->>Guardian: Validate Action
        Guardian-->>Module: Approval
        Module->>Memory: Store Result
        Module->>Brain: Return Result
        Brain->>Response: Consolidate
        Brain->>API: Send Response
        API->>User: Final Response
    else Request Rejected
        API->>User: Rejection + Reason
    end
```

## Module Interaction Map

```mermaid
graph LR
    subgraph "Consciousness Cluster"
        C1[Awareness Engine]
        C2[Reflection System]
        C3[State Manager]
        C1 <--> C2
        C2 <--> C3
    end
    
    subgraph "Memory Cluster"
        M1[DNA Helix Memory]
        M2[Fold Engine]
        M3[Drift Detector]
        M1 <--> M2
        M2 <--> M3
        M3 --> M1
    end
    
    subgraph "Reasoning Cluster"
        R1[Causal Inference]
        R2[Logic Engine]
        R3[Goal Processing]
        R1 --> R2
        R2 --> R3
    end
    
    subgraph "Creative Cluster"
        D1[Dream Engine]
        D2[Chaos Generator]
        D3[Pattern Extractor]
        D1 <--> D2
        D2 --> D3
    end
    
    C1 -.->|GLYPH| M1
    C3 -.->|GLYPH| R1
    R3 -.->|GLYPH| D1
    M3 -.->|GLYPH| C2
    D3 -.->|GLYPH| M2
```

## Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        L1[Application Security]
        L2[Guardian Protection]
        L3[Module Isolation]
        L4[Infrastructure Security]
    end
    
    subgraph "Application Security"
        A1[Input Validation]
        A2[Rate Limiting]
        A3[Token Auth]
    end
    
    subgraph "Guardian Protection"
        G1[Ethics Validation]
        G2[Threat Detection]
        G3[Behavioral Analysis]
        G4[Symbolic Firewall]
    end
    
    subgraph "Module Isolation"
        M1[Capability Control]
        M2[Resource Quotas]
        M3[Sandbox Execution]
    end
    
    subgraph "Infrastructure Security"
        I1[Network Segmentation]
        I2[Encryption]
        I3[Key Management]
        I4[Audit Logging]
    end
    
    L1 --> A1 & A2 & A3
    L2 --> G1 & G2 & G3 & G4
    L3 --> M1 & M2 & M3
    L4 --> I1 & I2 & I3 & I4
```

## Memory Architecture

```mermaid
graph TD
    subgraph "DNA Helix Memory System"
        O[Origin Strand - Immutable]
        C[Current Strand - Mutable]
        D[Drift Detector]
        R[Repair System]
        
        O --> D
        C --> D
        D -->|High Drift| R
        R -->|Repair| C
    end
    
    subgraph "Memory Contexts"
        MC[Core Memory]
        ME[Emotional Context]
        MT[Temporal Context]
        MCA[Causal Context]
    end
    
    subgraph "Storage Layers"
        HV[Helix Vault]
        PS[(PostgreSQL)]
        RD[(Redis Cache)]
        S3[(Object Storage)]
    end
    
    C --> MC & ME & MT & MCA
    MC --> HV
    HV --> PS
    HV --> RD
    HV --> S3
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Core Namespace"
            BHP[Brain Hub Pods x3]
            GSP[Guardian Pods x5]
            AGP[API Gateway Pods x3]
        end
        
        subgraph "Module Namespace"
            CP[Consciousness Pods]
            MP[Memory Pods]
            RP[Reasoning Pods]
            DP[Dream Engine Pods]
        end
        
        subgraph "Data Namespace"
            PG[PostgreSQL Cluster]
            RDS[Redis Cluster]
            ES[Elasticsearch]
        end
        
        subgraph "Monitoring"
            PROM[Prometheus]
            GRAF[Grafana]
            ALERT[AlertManager]
        end
    end
    
    subgraph "External"
        LB[Load Balancer]
        CDN[CDN]
        DNS[DNS]
    end
    
    DNS --> LB
    LB --> AGP
    CDN --> Static[Static Assets]
    
    AGP --> BHP
    BHP --> GSP
    BHP --> CP & MP & RP & DP
    
    MP --> PG & RDS
    CP --> RDS
    
    PROM --> All
    GRAF --> PROM
    ALERT --> PROM
```

## Performance Flow

```mermaid
graph LR
    subgraph "Request Path"
        REQ[Request] -->|10ms| API[API Gateway]
        API -->|50ms| BH[Brain Hub]
        BH -->|100ms| MOD[Modules]
        MOD -->|20ms| MEM[Memory]
        MEM -->|30ms| RESP[Response]
    end
    
    subgraph "Optimization Points"
        O1[Caching - Redis]
        O2[Parallel Processing]
        O3[Connection Pooling]
        O4[Query Optimization]
    end
    
    API -.-> O1
    BH -.-> O2
    MOD -.-> O3
    MEM -.-> O4
```

## State Management

```mermaid
stateDiagram-v2
    [*] --> Initializing
    Initializing --> Ready: All Modules Loaded
    Ready --> Processing: Request Received
    Processing --> GuardianCheck: Initial Validation
    GuardianCheck --> Processing: Approved
    GuardianCheck --> Rejected: Denied
    Processing --> ModuleExecution: Routed
    ModuleExecution --> Consolidation: Results Ready
    Consolidation --> FinalCheck: Guardian Validation
    FinalCheck --> Response: Approved
    FinalCheck --> Rejected: Denied
    Response --> Ready: Complete
    Rejected --> Ready: Logged
    
    state Processing {
        [*] --> Parsing
        Parsing --> GLYPHGeneration
        GLYPHGeneration --> Routing
    }
    
    state ModuleExecution {
        [*] --> Parallel
        Parallel --> Sequential
        Sequential --> Aggregation
    }
```

## Error Handling Flow

```mermaid
graph TD
    E[Error Detected] --> T{Error Type?}
    
    T -->|Validation| V[Validation Error]
    T -->|Guardian| G[Guardian Rejection]
    T -->|Module| M[Module Failure]
    T -->|System| S[System Error]
    
    V --> VH[Return 400 Bad Request]
    G --> GH[Log + Return 403 Forbidden]
    M --> MH{Retry?}
    S --> SH[Circuit Breaker]
    
    MH -->|Yes| R[Retry with Backoff]
    MH -->|No| F[Failover to Backup]
    
    R --> Success[Success]
    R --> Fail[Max Retries]
    
    SH --> Alert[Alert Ops Team]
    SH --> Degrade[Graceful Degradation]
    
    Success --> Log[Log Recovery]
    Fail --> Log
    F --> Log
    Degrade --> Log
```

## Module Lifecycle

```mermaid
graph LR
    subgraph "Module Lifecycle"
        Init[Initialize] --> Reg[Register with Guardian]
        Reg --> Load[Load Configuration]
        Load --> Ready[Ready State]
        Ready --> Proc[Process Requests]
        Proc --> Ready
        Ready --> Pause[Pause for Update]
        Pause --> Update[Hot Reload]
        Update --> Ready
        Ready --> Term[Terminate]
        Term --> Clean[Cleanup]
        Clean --> [*]
    end
    
    subgraph "Health Monitoring"
        Ready -.-> HC[Health Check]
        HC -->|Healthy| OK[Continue]
        HC -->|Unhealthy| Restart[Restart Module]
        Restart --> Init
    end
```

These diagrams provide a visual representation of LUKHAS 's architecture, showing:
1. Overall system structure and layers
2. Data flow through the system
3. Module interactions and dependencies
4. Security architecture
5. Memory system design
6. Deployment topology
7. Performance considerations
8. State management
9. Error handling
10. Module lifecycle management