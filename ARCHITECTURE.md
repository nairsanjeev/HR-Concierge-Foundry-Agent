# HR Concierge Agent — Architecture & Microsoft Platform Value

## Executive Summary

The HR Concierge Agent leverages the **Microsoft AI platform** to deliver an intelligent, enterprise-grade HR assistant that handles personal data changes and grievance screening. Built entirely on Azure AI Foundry as a **native prompt agent**, it demonstrates how Microsoft's unified AI stack eliminates integration complexity while delivering security, governance, and scalability out of the box.

---

## Solution Architecture

```mermaid
graph TB
    subgraph "Employee Touchpoints"
        A[👤 Employee] -->|Chat| B[Microsoft Teams]
        A -->|Web| C[Foundry Playground]
        A -->|API| D[Custom Portal]
    end

    subgraph "Azure AI Foundry"
        B --> E[HR Concierge Agent]
        C --> E
        D --> E
        
        E -->|Native Prompt Agent| F[gpt-5.4-mini<br/>DataZoneStandard]
        E -->|Tool Call| G[get_change_type_guidance]
        E -->|Tool Call| H[screen_grievance]
    end

    subgraph "Knowledge Layer"
        E -.->|Grounded in| I[Azure AI Search<br/>hr-knowledge-base]
        I -->|Indexed from| J[SharePoint Online<br/>HR Policy Docs]
        I -->|Indexed from| K[ServiceNow<br/>KB Articles]
    end

    subgraph "Action Layer"
        G -->|Deep Link| L[Workday ESS Portal]
        H -->|Deep Link| M[Workday ERLR Intake]
        H -->|Deep Link| N[Workday GOOS Request]
    end

    subgraph "Enterprise Foundation"
        O[Microsoft Entra ID<br/>Authentication & RBAC]
        P[Azure Monitor<br/>Observability]
        Q[Content Safety<br/>Responsible AI]
    end

    O -.-> E
    P -.-> E
    Q -.-> F

    style E fill:#0078d4,color:#fff
    style F fill:#50e6ff,color:#000
    style I fill:#ffb900,color:#000
```

---

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant Emp as Employee
    participant Agent as HR Concierge Agent
    participant LLM as gpt-5.4-mini
    participant Tool as Function Tools
    participant Search as Azure AI Search
    participant WD as Workday

    Emp->>Agent: "I need to change my legal name after marriage"
    Agent->>LLM: Process with system prompt + HR knowledge
    LLM->>Agent: Tool call: get_change_type_guidance(legal_name)
    Agent->>Tool: Execute function
    Tool-->>Agent: {tier: "Complex", docs: "marriage certificate", timeline: "3-5 days", link: "..."}
    Agent->>LLM: Incorporate tool response
    LLM-->>Agent: Formatted guidance with empathy
    Agent-->>Emp: "Congratulations! For a legal name change, you'll need..."
    
    Note over Emp,WD: Employee clicks deep link
    Emp->>WD: Opens HR Service Center form
```

---

## Grievance Screening Flow

```mermaid
flowchart TD
    A[Employee raises<br/>workplace concern] --> B{Agent asks<br/>clarifying questions}
    
    B -->|Involves misconduct| C{What type?}
    B -->|Workplace friction| D[Route to GOOS]
    B -->|Ambiguous| E[Ask follow-up<br/>questions]
    
    C -->|Harassment| F[Route to ERLR]
    C -->|Discrimination| F
    C -->|Retaliation| F
    C -->|Threats/Violence| F
    C -->|Ethical Violation| F
    C -->|Safety Issue| F
    C -->|Accommodation| F
    C -->|Bullying| F
    
    D --> G[GOOS Intake<br/>Voluntary · Mediation<br/>1-2 week resolution]
    F --> H[ERLR Intake<br/>Confidential · Investigation<br/>48hr case assignment]
    
    E -->|Clarified as misconduct| C
    E -->|Clarified as friction| D

    style F fill:#e74c3c,color:#fff
    style D fill:#27ae60,color:#fff
    style H fill:#e74c3c,color:#fff
    style G fill:#27ae60,color:#fff
```

---

## Personal Data Change Routing

```mermaid
flowchart LR
    A[Employee Request] --> B{Change Type?}
    
    B --> C[Tier 1: ESS<br/>Self-Service]
    B --> D[Tier 2: Complex<br/>HR Service Center]
    
    C --> C1[Emergency Contact]
    C --> C2[Home Address]
    C --> C3[Preferred Name]
    C --> C4[Marital Status]
    C --> C5[Pronouns]
    
    D --> D1[Legal Name]
    D --> D2[Passport/Visa]
    D --> D3[Bank Details]
    D --> D4[Government ID]
    D --> D5[Photo]
    D --> D6[Licenses/Certs]
    
    C1 & C2 & C3 & C4 & C5 --> E[✅ Immediate<br/>No Docs Required]
    D1 & D2 & D3 & D4 & D5 & D6 --> F[📋 3-5 Days<br/>Documentation Required]

    style C fill:#27ae60,color:#fff
    style D fill:#f39c12,color:#fff
    style E fill:#27ae60,color:#fff
    style F fill:#f39c12,color:#fff
```

---

## Microsoft Platform Value Proposition

```mermaid
mindmap
  root((Microsoft<br/>AI Platform<br/>Value))
    Unified AI Stack
      Single control plane
      One identity model
      Consistent APIs
      No vendor lock-in between services
    Enterprise Security
      Entra ID RBAC
      Data residency control
      Content Safety built-in
      No data leaves tenant
    Speed to Value
      Native agent — no containers
      Pre-built tool types
      Managed inference
      Zero infrastructure to maintain
    Knowledge Unification
      SharePoint connector
      ServiceNow indexing
      Azure AI Search semantic
      Single knowledge layer
    Responsible AI
      Content filtering
      Jailbreak protection
      PII detection
      Audit trail
    Scalability
      DataZone auto-scaling
      Global model routing
      Multi-region failover
      Pay-per-token economics
```

---

## Platform Comparison: Why Microsoft?

```mermaid
graph LR
    subgraph "Traditional Approach"
        T1[Custom LLM Hosting] --> T2[Build RAG Pipeline]
        T2 --> T3[Custom Auth Layer]
        T3 --> T4[Custom Monitoring]
        T4 --> T5[Custom Safety Filters]
        T5 --> T6[Custom Deployment]
    end

    subgraph "Microsoft AI Foundry"
        M1[Managed Model<br/>Deployment] --> M2[Native Search<br/>Integration]
        M2 --> M3[Entra ID<br/>Built-in]
        M3 --> M4[Azure Monitor<br/>Built-in]
        M4 --> M5[Content Safety<br/>Built-in]
        M5 --> M6[One-click<br/>Publish]
    end

    T6 -.->|"Months of work<br/>Multiple teams"| Result1[Production Agent]
    M6 -.->|"Hours to deploy<br/>Single developer"| Result2[Production Agent]

    style Result1 fill:#e74c3c,color:#fff
    style Result2 fill:#27ae60,color:#fff
```

---

## Detailed Component Architecture

### Azure AI Foundry — The Orchestration Layer

```mermaid
graph TB
    subgraph "Azure AI Foundry Project: hr-concierge-project"
        direction TB
        
        subgraph "Agent Layer"
            AG[HR Concierge<br/>Native Prompt Agent<br/>asst_AR1WuyJx8uslI2GOgZjA4hAJ]
        end

        subgraph "Model Layer"
            MD[gpt-5.4-mini<br/>Deployment: gpt-54-mini<br/>DataZoneStandard SKU]
        end

        subgraph "Tool Layer"
            T1[get_change_type_guidance<br/>Personal data routing]
            T2[screen_grievance<br/>ERLR vs GOOS screening]
        end

        subgraph "Connection Layer"
            CN[Azure AI Search Connection<br/>hr-concierge-search]
        end
    end

    subgraph "Resource Group: rg-hr-concierge"
        AI[Microsoft.CognitiveServices<br/>hr-concierge-ai<br/>Kind: AIServices / S0]
        SR[Microsoft.Search<br/>hr-concierge-search<br/>SKU: Basic]
    end

    AG --> MD
    AG --> T1
    AG --> T2
    AG -.-> CN
    CN --> SR
    AI --> AG

    style AG fill:#0078d4,color:#fff
    style AI fill:#0078d4,color:#fff
    style MD fill:#50e6ff,color:#000
```

### Knowledge Architecture

```mermaid
graph TB
    subgraph "Source Systems"
        SP[SharePoint Online<br/>m365cpi47937014.sharepoint.com<br/>/sites/JohnsonandJohnsonHR]
        SN[ServiceNow<br/>copilota2a.service-now.com<br/>Knowledge Base]
    end

    subgraph "Documents"
        SP --> D1[ESS Guide]
        SP --> D2[Complex Changes Policy]
        SP --> D3[Grievance/ERLR Policy]
        SP --> D4[GOOS Resolution Guide]
        SP --> D5[HR Service Catalog]
        
        SN --> D6[Emergency Contact Steps]
        SN --> D7[Legal Name Process]
        SN --> D8[Direct Deposit Guide]
        SN --> D9[Grievance Filing Steps]
        SN --> D10[GOOS Request Guide]
        SN --> D11[Preferred Name Steps]
        SN --> D12[Passport/Visa Steps]
        SN --> D13[Home Address Steps]
    end

    subgraph "Azure AI Search"
        IDX[Index: hr-knowledge-base<br/>13 documents<br/>Semantic ranking enabled]
        D1 & D2 & D3 & D4 & D5 --> IDX
        D6 & D7 & D8 & D9 & D10 & D11 & D12 & D13 --> IDX
    end

    subgraph "Agent Consumption"
        IDX -->|Semantic Search| AG[HR Concierge Agent]
    end

    style IDX fill:#ffb900,color:#000
    style AG fill:#0078d4,color:#fff
```

---

## Security & Governance Architecture

```mermaid
graph TB
    subgraph "Identity & Access"
        E[Microsoft Entra ID<br/>Tenant: 7672a31f-...-601c2c1451cc]
        E --> R1[Azure AI Developer<br/>Agent CRUD]
        E --> R2[Cognitive Services User<br/>Data-plane access]
        E --> R3[Search Index Data Reader<br/>Knowledge queries]
    end

    subgraph "Data Protection"
        DP1[Data stays in Azure tenant]
        DP2[No training on customer data]
        DP3[Encryption at rest & in transit]
        DP4[Customer-managed keys available]
    end

    subgraph "Responsible AI"
        RAI1[Content Safety filters<br/>Hate, Violence, Sexual, Self-harm]
        RAI2[Jailbreak detection]
        RAI3[PII detection & redaction]
        RAI4[Groundedness checks]
    end

    subgraph "Audit & Compliance"
        AU1[Azure Monitor logs]
        AU2[Agent conversation traces]
        AU3[Tool invocation audit]
        AU4[Model usage metrics]
    end

    style E fill:#0078d4,color:#fff
```

---

## Value Delivery: Microsoft Platform Benefits

### 1. Unified Identity — Zero Auth Code

```mermaid
graph LR
    A[Employee] -->|SSO| B[Microsoft Entra ID]
    B -->|Same token| C[Teams]
    B -->|Same token| D[SharePoint]
    B -->|Same token| E[AI Foundry Agent]
    B -->|Same token| F[Azure AI Search]
    
    style B fill:#0078d4,color:#fff
```

**Value**: No custom authentication. Employee's existing Microsoft 365 identity grants access to the agent, knowledge base, and all integrated services. One login, one session, one identity.

---

### 2. Knowledge Unification — Connect, Don't Migrate

```mermaid
graph TD
    subgraph "Before: Siloed Knowledge"
        B1[SharePoint<br/>Policies] 
        B2[ServiceNow<br/>How-To's]
        B3[Workday<br/>Procedures]
        B1 -.-|"Employees search<br/>3 systems"| X[😫 Frustrated Employee]
    end

    subgraph "After: Unified via Azure AI Search"
        A1[SharePoint] --> S[Azure AI Search<br/>Semantic Index]
        A2[ServiceNow] --> S
        A3[Workday Docs] --> S
        S --> AG[HR Concierge<br/>"Just ask me"]
        AG --> Y[😊 Guided Employee]
    end

    style S fill:#ffb900,color:#000
    style AG fill:#0078d4,color:#fff
```

**Value**: Employees don't need to know *where* information lives. The agent searches across SharePoint, ServiceNow, and Workday documentation simultaneously, returning one clear answer.

---

### 3. Native Agent — No Infrastructure

```mermaid
graph TD
    subgraph "Hosted Agent (Complex)"
        H1[Write agent code] --> H2[Build Docker container]
        H2 --> H3[Push to ACR]
        H3 --> H4[Deploy to compute]
        H4 --> H5[Manage scaling]
        H5 --> H6[Monitor health]
        H6 --> H7[Patch & update]
    end

    subgraph "Native Prompt Agent (Simple) ✅"
        N1[Define instructions] --> N2[Configure tools]
        N2 --> N3[Deploy via API]
        N3 --> N4[Done. ✨]
    end

    style N4 fill:#27ae60,color:#fff
    style H7 fill:#e74c3c,color:#fff
```

**Value**: Native prompt agents run entirely within Foundry's managed infrastructure. No Docker, no Kubernetes, no patching, no scaling configuration. The platform handles all operational concerns.

---

### 4. Responsible AI — Built-in Guardrails

```mermaid
graph LR
    A[Employee Input] --> B[Content Safety<br/>Filter]
    B -->|Safe| C[Agent Processing]
    B -->|Blocked| D[Safe Response]
    C --> E[Model Response]
    E --> F[Output Safety<br/>Filter]
    F -->|Safe| G[Employee Sees Response]
    F -->|Blocked| H[Filtered Response]

    style B fill:#e74c3c,color:#fff
    style F fill:#e74c3c,color:#fff
```

**Value**: Especially critical for HR grievance handling. Content Safety ensures the agent never generates inappropriate content, maintains confidentiality boundaries, and handles sensitive topics (harassment, discrimination) with appropriate care — all without custom code.

---

### 5. Enterprise Scale — DataZone Model Deployment

```mermaid
graph TB
    subgraph "DataZoneStandard Deployment"
        A[Request] --> B{Azure Traffic Manager}
        B --> C[Region 1<br/>Model Instance]
        B --> D[Region 2<br/>Model Instance]
        B --> E[Region N<br/>Model Instance]
    end
    
    F[Auto-scaling<br/>No capacity planning] -.-> B
    G[Pay-per-token<br/>No idle costs] -.-> B
    H[SLA-backed<br/>99.9% uptime] -.-> B

    style B fill:#0078d4,color:#fff
```

**Value**: DataZoneStandard deployment automatically routes requests across Azure regions for optimal latency and availability. No capacity planning, no over-provisioning, no cold starts.

---

## Cost Efficiency Analysis

| Component | Microsoft Platform | DIY Alternative | Savings |
|-----------|-------------------|-----------------|---------|
| **Model Hosting** | Pay-per-token (no idle cost) | GPU VMs 24/7 ($2-5K/mo) | ~90% |
| **Search Infrastructure** | Basic SKU ($75/mo) | Self-managed Elastic ($500+/mo) | ~85% |
| **Authentication** | Entra ID (included in M365) | Custom OAuth + user mgmt ($200+/mo) | 100% |
| **Agent Runtime** | Managed (included) | Container hosting ($200-500/mo) | 100% |
| **Monitoring** | Azure Monitor (included) | DataDog/Splunk ($300+/mo) | 100% |
| **Content Safety** | Built-in (included) | Custom filters + moderation ($500+/mo) | 100% |
| **Total Estimated** | **~$100-200/mo** | **$4,000-7,000/mo** | **~97%** |

---

## Deployment Topology

```mermaid
graph TB
    subgraph "Azure Subscription: ME-M365CPI47937014-jaysen-1"
        subgraph "Resource Group: rg-hr-concierge (eastus2)"
            AI[AI Services: hr-concierge-ai<br/>SKU: S0<br/>Region: eastus2]
            
            subgraph "Project: hr-concierge-project"
                AG[Agent: hr-concierge<br/>ID: asst_AR1WuyJx8uslI2GOgZjA4hAJ]
                DEP[Model Deployment: gpt-54-mini<br/>gpt-5.4-mini | 2026-03-17<br/>DataZoneStandard | Capacity: 10]
            end
        end

        subgraph "Resource Group: rg-hr-concierge (eastus)"
            SR[AI Search: hr-concierge-search<br/>SKU: Basic<br/>Region: eastus]
            IDX[Index: hr-knowledge-base<br/>13 documents]
        end
    end

    subgraph "Microsoft 365 Tenant"
        SP[SharePoint: JohnsonandJohnsonHR<br/>5 HR policy documents]
    end

    subgraph "External SaaS"
        SN[ServiceNow: copilota2a<br/>8 KB articles]
    end

    AI --> AG
    AG --> DEP
    AG -.-> SR
    SR --> IDX
    SP -.->|Indexed| IDX
    SN -.->|Indexed| IDX

    style AI fill:#0078d4,color:#fff
    style AG fill:#50e6ff,color:#000
    style SR fill:#ffb900,color:#000
```

---

## Integration Roadmap

```mermaid
gantt
    title HR Concierge — Enhancement Roadmap
    dateFormat  YYYY-MM-DD
    
    section Phase 1 (Current)
    Native Prompt Agent               :done, p1a, 2026-05-15, 1d
    Function Tools (2)                :done, p1b, 2026-05-15, 1d
    Azure AI Search Knowledge         :done, p1c, 2026-05-15, 1d
    
    section Phase 2 (Next Sprint)
    SharePoint Grounding Tool         :p2a, 2026-05-20, 5d
    Teams Channel Deployment          :p2b, 2026-05-22, 3d
    Conversation Analytics            :p2c, 2026-05-25, 4d
    
    section Phase 3 (Month 2)
    Workday API Integration           :p3a, 2026-06-01, 10d
    ServiceNow Ticket Creation        :p3b, 2026-06-05, 7d
    Multi-language Support            :p3c, 2026-06-10, 5d
    
    section Phase 4 (Month 3)
    Proactive Notifications           :p4a, 2026-07-01, 10d
    Manager Dashboard                 :p4b, 2026-07-05, 10d
    Continuous Evaluation             :p4c, 2026-07-10, 7d
```

---

## Summary: Microsoft Platform Differentiators

| Differentiator | How It Applies to HR Concierge |
|----------------|-------------------------------|
| **Unified Identity** | Employees use existing M365 credentials. No new accounts. |
| **Native Agent Model** | No containers, no DevOps — just prompt + tools = production agent |
| **Semantic Search** | One index spans SharePoint + ServiceNow. Employee asks once. |
| **Responsible AI** | Built-in safety for sensitive HR topics (grievances, discrimination) |
| **Data Residency** | All data stays within the Azure tenant. No external API calls for core logic. |
| **Enterprise RBAC** | Granular role assignments. HR admins manage agent, employees consume. |
| **Pay-per-Use** | Token-based pricing. No GPU reservations. Cost scales with actual usage. |
| **Teams Integration** | One-click publish to where employees already work |
| **Observability** | Azure Monitor traces every conversation, tool call, and model response |
| **Compliance** | SOC 2, ISO 27001, HIPAA BAA, FedRAMP — inherited from platform |

---

*Document generated: May 15, 2026*  
*Agent: HR Concierge v1.0.0*  
*Platform: Azure AI Foundry (Native Prompt Agent)*
