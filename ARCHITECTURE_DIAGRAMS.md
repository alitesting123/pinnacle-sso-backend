# Architecture Diagrams (Mermaid Code)

This document contains architecture diagrams as code using Mermaid syntax. These diagrams can be rendered in GitHub, GitLab, VS Code, and other Markdown viewers.

## Table of Contents
1. [System Context Diagram (C4 Level 1)](#1-system-context-diagram-c4-level-1)
2. [Container Diagram (C4 Level 2)](#2-container-diagram-c4-level-2)
3. [Component Diagram (C4 Level 3)](#3-component-diagram-c4-level-3)
4. [Deployment Architecture](#4-deployment-architecture)
5. [RAG Question Flow Sequence](#5-rag-question-flow-sequence)
6. [Auto-Scaling State Machine](#6-auto-scaling-state-machine)
7. [Database Entity Relationship](#7-database-entity-relationship)
8. [AWS Infrastructure](#8-aws-infrastructure)

---

## 1. System Context Diagram (C4 Level 1)

Shows how the system fits into the broader ecosystem.

```mermaid
C4Context
    title System Context Diagram - Pinnacle SSO Backend

    Person(customer, "Event Client", "Client reviewing proposals and asking questions")
    Person(admin, "Admin User", "Staff managing proposals and answering questions")

    System(pinnacle, "Pinnacle SSO Backend", "Event planning proposal management with AI-powered Q&A")

    System_Ext(cognito, "AWS Cognito", "User authentication and SSO")
    System_Ext(claude, "Anthropic Claude API", "AI question answering and RAG")
    System_Ext(database, "Supabase PostgreSQL", "Proposal and user data storage")
    System_Ext(email, "Gmail SMTP", "Email notifications")
    System_Ext(frontend, "Amplify Frontend", "React/Vue web application")

    Rel(customer, frontend, "Views proposals, asks questions", "HTTPS")
    Rel(admin, frontend, "Manages proposals", "HTTPS")
    Rel(frontend, pinnacle, "Makes API calls", "HTTPS/JSON")
    Rel(pinnacle, cognito, "Authenticates users", "HTTPS")
    Rel(pinnacle, claude, "Generates AI answers", "HTTPS")
    Rel(pinnacle, database, "Reads/writes data", "PostgreSQL")
    Rel(pinnacle, email, "Sends notifications", "SMTP/TLS")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="2")
```

---

## 2. Container Diagram (C4 Level 2)

Shows the high-level technical architecture.

```mermaid
C4Container
    title Container Diagram - Pinnacle SSO Backend

    Person(user, "User", "Client or Admin")

    Container_Boundary(aws, "AWS Cloud") {
        Container(alb, "Application Load Balancer", "AWS ALB", "Routes requests, SSL/TLS termination, health checks")

        Container_Boundary(eb, "Elastic Beanstalk Environment") {
            Container(nginx, "Nginx", "Reverse Proxy", "Request routing, static files, timeouts")
            Container(gunicorn, "Gunicorn", "WSGI Server", "4 workers, Uvicorn worker class")
            Container(fastapi, "FastAPI Application", "Python 3.11", "REST API endpoints, business logic")
            Container(rag, "RAG Service", "Python Module", "Claude AI integration, embeddings, FAISS")
        }

        ContainerDb(redis, "Redis Cache", "ElastiCache", "Session storage, rate limiting, caching")
    }

    ContainerDb_Ext(postgres, "PostgreSQL", "Supabase", "Proposals, questions, users")
    System_Ext(claude_api, "Claude API", "Anthropic", "AI answer generation")
    System_Ext(cognito, "AWS Cognito", "Auth Service", "User authentication")

    Rel(user, alb, "HTTPS requests", "HTTPS")
    Rel(alb, nginx, "Forwards requests", "HTTP")
    Rel(nginx, gunicorn, "Proxy", "HTTP")
    Rel(gunicorn, fastapi, "WSGI", "Python")
    Rel(fastapi, rag, "Calls", "Python")
    Rel(fastapi, postgres, "SQL queries", "PostgreSQL/SSL")
    Rel(fastapi, redis, "Cache ops", "Redis Protocol")
    Rel(rag, claude_api, "API calls", "HTTPS/JSON")
    Rel(fastapi, cognito, "Verify tokens", "HTTPS")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

---

## 3. Component Diagram (C4 Level 3)

Shows the internal components of the FastAPI application.

```mermaid
C4Component
    title Component Diagram - FastAPI Application

    Container_Boundary(fastapi, "FastAPI Application") {
        Component(router, "API Router", "FastAPI Router", "Route definitions and middleware")

        Component(auth, "Auth Module", "Python", "JWT validation, Cognito integration")
        Component(proposals, "Proposal Service", "Python", "Proposal CRUD operations")
        Component(questions, "Question Service", "Python", "Q&A management")
        Component(users, "User Service", "Python", "User management")
        Component(email, "Email Service", "Python", "SMTP email notifications")

        Component_Boundary(rag_boundary, "RAG Service") {
            Component(classifier, "Question Classifier", "Python", "Categorizes questions")
            Component(embedder, "Embedding Generator", "Sentence Transformers", "Creates vector embeddings")
            Component(faiss, "Vector Search", "FAISS", "Semantic similarity search")
            Component(claude, "Claude Client", "Anthropic SDK", "AI answer generation")
        }

        Component(models, "SQLAlchemy Models", "ORM", "Database models")
        Component(config, "Configuration", "Pydantic Settings", "Environment config")
    }

    ComponentDb_Ext(db, "PostgreSQL", "Database", "Data persistence")
    System_Ext(claude_api, "Claude API", "External AI service")

    Rel(router, auth, "Validates", "Python")
    Rel(router, proposals, "Calls", "Python")
    Rel(router, questions, "Calls", "Python")
    Rel(router, users, "Calls", "Python")

    Rel(questions, classifier, "Classifies question", "Python")
    Rel(questions, embedder, "Generates embedding", "Python")
    Rel(questions, faiss, "Searches vectors", "Python")
    Rel(questions, claude, "Gets AI answer", "Python")

    Rel(proposals, models, "Uses", "Python")
    Rel(questions, models, "Uses", "Python")
    Rel(users, models, "Uses", "Python")
    Rel(models, db, "Queries", "SQL")

    Rel(claude, claude_api, "API call", "HTTPS")
    Rel(router, config, "Reads", "Python")
```

---

## 4. Deployment Architecture

Shows how the system is deployed on AWS infrastructure.

```mermaid
graph TB
    subgraph Internet["🌐 Internet"]
        Users[("👥 Users")]
    end

    subgraph AWS["☁️ AWS Cloud - us-east-1"]
        subgraph CDN["CDN Layer (Optional)"]
            CF[CloudFront CDN<br/>Global Edge Locations]
        end

        subgraph LoadBalancer["Load Balancing"]
            ALB[Application Load Balancer<br/>Multi-AZ<br/>SSL/TLS Termination]
        end

        subgraph AZ1["Availability Zone 1a"]
            subgraph EB1["Elastic Beanstalk"]
                EC2_1["EC2 Instance<br/>t3.medium<br/>2 vCPU, 4GB RAM"]
                subgraph App1["Application Stack"]
                    Nginx1[Nginx]
                    Gunicorn1[Gunicorn<br/>4 Workers]
                    FastAPI1[FastAPI<br/>+ RAG Service]
                end
            end
            Redis1[(Redis Primary<br/>ElastiCache<br/>cache.t3.micro)]
        end

        subgraph AZ2["Availability Zone 1b"]
            subgraph EB2["Elastic Beanstalk"]
                EC2_2["EC2 Instance<br/>t3.medium<br/>2 vCPU, 4GB RAM"]
                subgraph App2["Application Stack"]
                    Nginx2[Nginx]
                    Gunicorn2[Gunicorn<br/>4 Workers]
                    FastAPI2[FastAPI<br/>+ RAG Service]
                end
            end
            Redis2[(Redis Replica<br/>ElastiCache<br/>Failover)]
        end

        subgraph Monitoring["Monitoring & Logging"]
            CW[CloudWatch<br/>Logs & Metrics]
            Alarms[CloudWatch Alarms<br/>Auto-Scaling Triggers]
        end
    end

    subgraph External["External Services"]
        Supabase[(Supabase PostgreSQL<br/>Multi-Region<br/>Connection Pooling)]
        Claude[Anthropic Claude API<br/>claude-3-haiku-20240307]
        Cognito[AWS Cognito<br/>User Pool<br/>SSO/OAuth]
    end

    Users -->|HTTPS| CF
    CF -->|HTTPS| ALB
    Users -.->|Direct| ALB

    ALB -->|HTTP| EC2_1
    ALB -->|HTTP| EC2_2

    EC2_1 --> Nginx1 --> Gunicorn1 --> FastAPI1
    EC2_2 --> Nginx2 --> Gunicorn2 --> FastAPI2

    FastAPI1 -->|SQL| Supabase
    FastAPI2 -->|SQL| Supabase

    FastAPI1 -->|Cache| Redis1
    FastAPI2 -->|Cache| Redis1
    Redis1 -.->|Replication| Redis2

    FastAPI1 -->|HTTPS| Claude
    FastAPI2 -->|HTTPS| Claude

    FastAPI1 -->|Verify JWT| Cognito
    FastAPI2 -->|Verify JWT| Cognito

    EC2_1 -.->|Logs| CW
    EC2_2 -.->|Logs| CW
    Alarms -.->|Scale| EB1
    Alarms -.->|Scale| EB2

    style AWS fill:#FF9900,stroke:#232F3E,stroke-width:3px,color:#fff
    style AZ1 fill:#3F8624,stroke:#1a472a,stroke-width:2px
    style AZ2 fill:#3F8624,stroke:#1a472a,stroke-width:2px
    style External fill:#E7157B,stroke:#8C0032,stroke-width:2px
```

---

## 5. RAG Question Flow Sequence

Shows the detailed flow of a RAG-enabled question from submission to answer.

```mermaid
sequenceDiagram
    actor Client
    participant ALB as Load Balancer
    participant App as FastAPI
    participant Classifier as Question Classifier
    participant Embedder as Sentence Transformers
    participant FAISS as FAISS Vector DB
    participant DB as PostgreSQL
    participant Claude as Claude API

    Note over Client,Claude: User Submits Question

    Client->>+ALB: POST /api/v1/proposals/{id}/questions<br/>{question_text: "What is total cost?"}
    ALB->>+App: Forward request

    App->>App: Validate request & auth
    App->>+DB: Fetch proposal data
    DB-->>-App: Proposal details

    Note over App,Classifier: Step 1: Classification (20ms)
    App->>+Classifier: classify_question(question)
    Classifier->>Classifier: Analyze keywords & complexity
    Classifier-->>-App: {category: "simple", auto_answer: true}

    alt Question is Simple or T&C (Auto-Answer)
        Note over App,Claude: Step 2: RAG Processing

        App->>+Embedder: Generate embedding<br/>for question (50ms)
        Embedder-->>-App: Vector [384 dimensions]

        App->>+FAISS: Semantic search<br/>against proposal content (10ms)
        FAISS-->>-App: Top 3 relevant chunks

        App->>+DB: Fetch context details (30ms)
        DB-->>-App: Section/item details

        Note over App,Claude: Step 3: AI Answer Generation
        App->>+Claude: Generate answer<br/>with context (500-1000ms)
        Claude-->>-App: AI-generated answer

        App->>App: Format response<br/>+ add sources

        Note over App,DB: Step 4: Save to Database
        App->>+DB: INSERT INTO proposal_questions<br/>{question, answer, ai_generated: true}
        DB-->>-App: Question saved

        App-->>ALB: 200 OK<br/>{question_id, answer, ai_generated: true}

    else Question is Complex (Human Review)
        Note over App,DB: Save for human review
        App->>+DB: INSERT INTO proposal_questions<br/>{question, status: "pending", ai_generated: false}
        DB-->>-App: Question saved

        App-->>ALB: 200 OK<br/>{question_id, status: "pending"}
    end

    ALB-->>-Client: Response

    Note over Client,Claude: Total Time:<br/>Simple: ~700ms | Complex: ~70ms
```

---

## 6. Auto-Scaling State Machine

Shows how the auto-scaling system responds to load.

```mermaid
stateDiagram-v2
    [*] --> Normal: Deploy

    state Normal {
        [*] --> Monitoring
        Monitoring --> Monitoring: CPU < 70%
    }

    Normal --> ScalingUp: CPU > 70%<br/>for 3 minutes

    state ScalingUp {
        [*] --> LaunchingInstance
        LaunchingInstance --> InstallingDeps: EC2 Started
        InstallingDeps --> DownloadingModels: Dependencies Installed
        DownloadingModels --> WarmingUp: Models Downloaded
        WarmingUp --> HealthCheck: Cache Warmed
        HealthCheck --> Ready: Health Check Pass
    }

    ScalingUp --> Scaled: Instance Ready<br/>(~4 minutes)

    state Scaled {
        [*] --> MonitoringHigh
        MonitoringHigh --> MonitoringHigh: 20% < CPU < 70%
    }

    Scaled --> ScalingDown: CPU < 20%<br/>for 5 minutes

    state ScalingDown {
        [*] --> DrainingConnections
        DrainingConnections --> RemovingFromLB: Connections Drained
        RemovingFromLB --> TerminatingInstance: Removed from ALB
    }

    ScalingDown --> Normal: Instance Terminated

    Scaled --> MaxCapacity: Instances = 4

    state MaxCapacity {
        [*] --> AtLimit
        AtLimit --> AtLimit: Cannot scale more
        note right of AtLimit
            Consider:
            - Upgrade instance type
            - Increase max instances
            - Optimize application
        end note
    }

    MaxCapacity --> Scaled: CPU normalized

    Normal --> Error: Health Check Failed
    Scaled --> Error: Health Check Failed

    state Error {
        [*] --> Unhealthy
        Unhealthy --> AutoRecovery: Trigger Recovery
        AutoRecovery --> LaunchingReplacement
        LaunchingReplacement --> Recovering
    }

    Error --> Normal: Recovery Complete
```

---

## 7. Database Entity Relationship

Shows the database schema relationships.

```mermaid
erDiagram
    PROPOSALS ||--o{ PROPOSAL_SECTIONS : has
    PROPOSALS ||--o{ PROPOSAL_LINE_ITEMS : contains
    PROPOSALS ||--o{ PROPOSAL_TIMELINE : schedules
    PROPOSALS ||--o{ PROPOSAL_LABOR : requires
    PROPOSALS ||--o{ PROPOSAL_QUESTIONS : receives
    PROPOSALS ||--o{ PROPOSAL_TEMP_LINKS : generates
    PROPOSALS ||--o{ PROPOSAL_SESSIONS : tracks

    PROPOSAL_SECTIONS ||--o{ PROPOSAL_LINE_ITEMS : contains

    PRE_APPROVED_USERS ||--o| ACTIVE_USERS : becomes

    PROPOSALS {
        uuid id PK
        string job_number UK
        string client_name
        string client_email
        string event_location
        date start_date
        date end_date
        decimal total_cost
        string status
        timestamp created_at
    }

    PROPOSAL_SECTIONS {
        uuid id PK
        uuid proposal_id FK
        string section_name
        string section_type
        int display_order
        decimal section_total
    }

    PROPOSAL_LINE_ITEMS {
        uuid id PK
        uuid section_id FK
        uuid proposal_id FK
        text description
        int quantity
        decimal unit_price
        decimal subtotal
    }

    PROPOSAL_QUESTIONS {
        uuid id PK
        uuid proposal_id FK
        string client_email
        text question_text
        text answer_text
        boolean ai_generated
        string status
        timestamp created_at
        timestamp answered_at
    }

    PROPOSAL_TIMELINE {
        uuid id PK
        uuid proposal_id FK
        datetime event_time
        text description
        string category
    }

    PROPOSAL_LABOR {
        uuid id PK
        uuid proposal_id FK
        string role
        int quantity
        decimal hourly_rate
        decimal total
    }

    PROPOSAL_TEMP_LINKS {
        uuid id PK
        uuid proposal_id FK
        string token UK
        datetime expires_at
        boolean is_active
    }

    PROPOSAL_SESSIONS {
        uuid id PK
        uuid proposal_id FK
        string session_id UK
        datetime accessed_at
    }

    PRE_APPROVED_USERS {
        string id PK
        string email UK
        string full_name
        json roles
        boolean is_active
    }

    ACTIVE_USERS {
        string user_id PK
        string email UK
        string pre_approved_id FK
        datetime last_login
    }
```

---

## 8. AWS Infrastructure

Shows the complete AWS infrastructure components.

```mermaid
graph TB
    subgraph Internet["🌐 Internet / Users"]
        Browser["Web Browser"]
        Mobile["Mobile App"]
        API["API Clients"]
    end

    subgraph Route53["Route 53 (DNS)"]
        DNS["api.pinnacle.com<br/>CNAME → ELB"]
    end

    subgraph ACM["Certificate Manager"]
        SSL["SSL/TLS Certificate<br/>*.pinnacle.com"]
    end

    subgraph VPC["VPC - us-east-1"]
        subgraph PublicSubnet["Public Subnets"]
            ALB["Application Load Balancer<br/>- SSL Termination<br/>- Health Checks<br/>- Path Routing"]
            NAT["NAT Gateway"]
        end

        subgraph PrivateSubnet1["Private Subnet 1a"]
            EC2_1["EC2 - t3.medium<br/>- Nginx<br/>- Gunicorn<br/>- FastAPI + RAG"]
        end

        subgraph PrivateSubnet2["Private Subnet 1b"]
            EC2_2["EC2 - t3.medium<br/>- Nginx<br/>- Gunicorn<br/>- FastAPI + RAG"]
        end

        subgraph CacheSubnet["ElastiCache Subnet"]
            Redis["Redis Cluster<br/>- Session Storage<br/>- Rate Limiting<br/>- cache.t3.micro"]
        end
    end

    subgraph EB["Elastic Beanstalk"]
        EBEnv["Environment<br/>pinnacle-sso-production"]
        ASG["Auto Scaling Group<br/>Min: 1, Max: 4<br/>Target: CPU 70%"]
        LC["Launch Configuration<br/>- Python 3.11<br/>- AL2<br/>- t3.medium"]
    end

    subgraph Monitoring["CloudWatch"]
        Logs["CloudWatch Logs<br/>- Application Logs<br/>- Access Logs<br/>- Error Logs"]
        Metrics["CloudWatch Metrics<br/>- CPU/Memory<br/>- Request Count<br/>- Response Time"]
        Alarms["CloudWatch Alarms<br/>- High CPU → Scale<br/>- 5xx Errors → Alert<br/>- Health → Recover"]
    end

    subgraph IAM["IAM"]
        Role["EC2 Instance Role<br/>- CloudWatch Logs<br/>- S3 Access<br/>- Secrets Manager"]
    end

    subgraph External["External Services"]
        Supabase[("Supabase PostgreSQL<br/>- pgBouncer<br/>- SSL/TLS<br/>- Backups")]
        Anthropic["Anthropic API<br/>- Claude Haiku<br/>- HTTPS"]
        Cognito["AWS Cognito<br/>- User Pool<br/>- JWT Tokens"]
        SMTP["Gmail SMTP<br/>- TLS<br/>- Port 587"]
    end

    Browser --> DNS
    Mobile --> DNS
    API --> DNS

    DNS --> SSL
    SSL --> ALB

    ALB --> EC2_1
    ALB --> EC2_2

    EC2_1 --> Redis
    EC2_2 --> Redis

    EC2_1 --> Supabase
    EC2_2 --> Supabase

    EC2_1 --> Anthropic
    EC2_2 --> Anthropic

    EC2_1 --> Cognito
    EC2_2 --> Cognito

    EC2_1 --> SMTP
    EC2_2 --> SMTP

    EC2_1 --> NAT
    EC2_2 --> NAT

    EBEnv --> ASG
    ASG --> LC
    ASG --> EC2_1
    ASG --> EC2_2

    EC2_1 -.-> Logs
    EC2_2 -.-> Logs
    EC2_1 -.-> Metrics
    EC2_2 -.-> Metrics

    Metrics --> Alarms
    Alarms -.-> ASG

    EC2_1 -.-> Role
    EC2_2 -.-> Role

    style VPC fill:#FF9900,stroke:#232F3E,stroke-width:3px
    style EB fill:#FF9900,stroke:#232F3E,stroke-width:2px
    style Monitoring fill:#FF4F8B,stroke:#8C0032,stroke-width:2px
    style External fill:#146EB4,stroke:#0E4D7A,stroke-width:2px
```

---

## Usage Instructions

### View in GitHub
Simply view this file on GitHub - Mermaid diagrams render automatically.

### View in VS Code
Install the "Markdown Preview Mermaid Support" extension:
```bash
code --install-extension bierner.markdown-mermaid
```

### Export as Images
Use the Mermaid CLI:
```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Export diagrams
mmdc -i ARCHITECTURE_DIAGRAMS.md -o output.png
```

### View Online
Copy any diagram code block to: https://mermaid.live/

### Customize
Edit the Mermaid code blocks and adjust:
- Colors using `style` commands
- Layout using `UpdateLayoutConfig`
- Text and labels
- Relationships and flows

---

## Diagram Legend

### C4 Diagrams
- **Person**: Human user (customer, admin)
- **System**: Software system
- **Container**: Deployable unit (service, database)
- **Component**: Code component (module, class)

### Graph Diagrams
- **Solid arrows**: Data/control flow
- **Dashed arrows**: Monitoring/logging
- **Colored boxes**: Logical groupings

### Sequence Diagrams
- **Timeline**: Top to bottom = time progression
- **Actors**: Users or external systems
- **Participants**: System components
- **Messages**: Interactions between components

---

**Generated**: 2025-12-05
**Version**: 1.0
**Format**: Mermaid v10+
**Maintainer**: Pinnacle Development Team
