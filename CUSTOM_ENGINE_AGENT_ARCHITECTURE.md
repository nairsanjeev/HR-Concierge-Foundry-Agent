# Custom Engine Agent Architecture — HR Concierge via M365 Copilot

## Executive Summary

This document details the architecture of the **HR Concierge Custom Engine Agent (CEA)** — an intelligent HR assistant that is surfaced through **Microsoft 365 Copilot** and powered by **Azure AI Foundry** as its custom AI orchestration engine. The agent uses the **Bot Framework** as its communication backbone, enabling employees to interact with it directly inside Microsoft Teams through the familiar Copilot experience.

A Custom Engine Agent is distinct from a Declarative Agent in that it brings its **own AI model and orchestration logic** rather than relying on the M365 Copilot orchestrator. This gives full control over the model, prompts, tools, grounding data, and conversation flow.

---

## What is a Custom Engine Agent?

```mermaid
graph LR
    subgraph "Declarative Agent"
        DA[M365 Copilot Orchestrator] -->|Controls model & reasoning| DAR[Response]
    end

    subgraph "Custom Engine Agent"
        CEA[Your Own AI Engine<br/>Azure AI Foundry] -->|You control model & reasoning| CEAR[Response]
    end

    style DA fill:#6c757d,color:#fff
    style CEA fill:#0078d4,color:#fff
```

| Aspect | Declarative Agent | Custom Engine Agent |
|--------|------------------|---------------------|
| **AI Orchestration** | M365 Copilot orchestrator | Your own engine (Azure AI Foundry) |
| **Model Selection** | Microsoft-managed | You choose (gpt-5.4-mini, GPT-4o, etc.) |
| **Prompt Control** | Limited instructions | Full system prompt & instruction control |
| **Tool Execution** | Copilot-managed plugins | Custom function tools, Azure AI Search, APIs |
| **Grounding** | Microsoft Graph, SharePoint | Any data source (Search, SQL, APIs, files) |
| **Conversation State** | Copilot-managed | Self-managed threads & context |
| **Use Case** | Simple Q&A, data retrieval | Complex workflows, multi-turn reasoning, domain agents |

The HR Concierge uses the **Custom Engine Agent** pattern because it requires:
- Domain-specific system prompts with detailed HR process logic
- Custom function tools (`get_change_type_guidance`, `screen_grievance`)
- Azure AI Search grounding across SharePoint and ServiceNow
- Multi-turn conversation management for grievance screening
- Full control over response tone, SLAs, and deep linking behavior

---

## End-to-End Architecture

```mermaid
graph TB
    subgraph "Microsoft 365 Copilot Surface"
        U[👤 Employee in Teams] -->|"@HR Concierge"| COP[Microsoft 365 Copilot]
        COP -->|Recognizes CEA| ROUTE[Agent Router]
    end

    subgraph "Bot Framework Channel"
        ROUTE -->|Activity forwarded| ABS[Azure Bot Service<br/>Bot Channel Registration]
        ABS -->|HTTPS POST| BFW[Bot Framework SDK<br/>App Service / Azure Functions]
    end

    subgraph "Custom Engine — Azure AI Foundry"
        BFW -->|Orchestrates via SDK| AGT[HR Concierge Agent<br/>Native Prompt Agent<br/>asst_kvvmzmqkQpF2Tfpe11NmFBzs]
        AGT -->|Inference| LLM[gpt-5.4-mini<br/>DataZoneStandard]
        AGT -->|Tool calls| T1[get_change_type_guidance]
        AGT -->|Tool calls| T2[screen_grievance]
        AGT -->|RAG queries| AIS[Azure AI Search<br/>hr-knowledge-base]
    end

    subgraph "Knowledge Sources"
        AIS -->|Indexed from| SP[SharePoint Online<br/>HR Policy Docs]
        AIS -->|Indexed from| SN[ServiceNow<br/>KB Articles]
    end

    subgraph "Action Endpoints"
        T1 -->|Deep link| WD1[Workday ESS Portal]
        T2 -->|Deep link| WD2[Workday ERLR/GOOS]
    end

    subgraph "Enterprise Services"
        EID[Microsoft Entra ID<br/>Authentication & SSO]
        MON[Azure Monitor<br/>Telemetry & Tracing]
        CS[Content Safety<br/>Input/Output Filtering]
    end

    EID -.-> ABS
    EID -.-> AGT
    MON -.-> BFW
    CS -.-> LLM

    style COP fill:#6f42c1,color:#fff
    style ABS fill:#0078d4,color:#fff
    style AGT fill:#0078d4,color:#fff
    style LLM fill:#50e6ff,color:#000
    style AIS fill:#ffb900,color:#000
```

---

## Component Deep Dive

### 1. Microsoft 365 Copilot — The Surface Layer

Microsoft 365 Copilot acts as the **front door** for the employee. When the HR Concierge is registered as a Custom Engine Agent, it appears as a selectable agent within the Copilot experience in Teams.

**How employees invoke it:**
- Type `@HR Concierge` in Microsoft Teams chat
- Select "HR Concierge" from the Copilot agent picker
- Ask a question in the Copilot side panel and have it routed to the agent

**What M365 Copilot does:**
1. Presents the agent in the Teams Copilot UI
2. Captures the user's message
3. Identifies that this is a Custom Engine Agent (not a Declarative Agent)
4. Forwards the entire conversation turn to the registered bot endpoint
5. Renders the bot's response back to the user in the Teams UI

M365 Copilot does **NOT** perform any AI reasoning for a CEA — it is purely a routing and rendering layer.

---

### 2. Azure Bot Service — The Communication Backbone

```mermaid
graph TB
    subgraph "Azure Bot Service"
        REG[Bot Channel Registration<br/>Microsoft App ID: {app-id}<br/>Messaging Endpoint: https://hr-bot.azurewebsites.net/api/messages]
        
        subgraph "Channels"
            CH1[Microsoft Teams]
            CH2[Microsoft 365 Copilot]
            CH3[Web Chat — optional]
        end
        
        REG --> CH1
        REG --> CH2
        REG --> CH3
    end
    
    subgraph "Authentication"
        AAD[Microsoft Entra ID App Registration<br/>Client ID + Secret<br/>Bot Framework auth tokens]
    end
    
    AAD --> REG

    style REG fill:#0078d4,color:#fff
```

**Azure Bot Service** provides:

| Capability | Description |
|-----------|-------------|
| **Channel Abstraction** | Single bot endpoint serves Teams, Copilot, Web Chat, etc. |
| **Authentication** | Validates tokens between M365 Copilot and your bot endpoint |
| **Message Routing** | Delivers Activities (messages, events) to your bot code |
| **Protocol Handling** | Manages the Bot Framework Protocol (JSON over HTTPS) |
| **Scaling** | Handles connection management across thousands of concurrent users |

**Registration details:**
- **App Type**: Multi-tenant or Single-tenant Entra ID app
- **Messaging Endpoint**: `https://<your-app-service>.azurewebsites.net/api/messages`
- **OAuth Connection**: Used for SSO token exchange with the employee's identity

---

### 3. Bot Framework SDK — The Application Layer

The Bot Framework SDK is the **code that runs your bot logic**. It receives Activities from Azure Bot Service and produces responses.

```mermaid
sequenceDiagram
    participant Teams as M365 Copilot / Teams
    participant ABS as Azure Bot Service
    participant Bot as Bot Framework App<br/>(App Service)
    participant Foundry as Azure AI Foundry<br/>HR Concierge Agent
    participant Tools as Function Tools
    participant Search as Azure AI Search

    Teams->>ABS: User message Activity
    ABS->>Bot: POST /api/messages<br/>{type: "message", text: "I need to change my name"}
    
    Bot->>Bot: Extract user message & conversation state
    Bot->>Foundry: Create thread + add message + run agent
    
    Foundry->>Foundry: LLM processes with system prompt
    Foundry->>Tools: Tool call: get_change_type_guidance("legal_name")
    Tools-->>Foundry: {tier: "Complex", docs: "marriage cert", link: "..."}
    Foundry->>Search: RAG query for name change policy
    Search-->>Foundry: Policy document chunks
    Foundry-->>Bot: Agent response with guidance + deep link
    
    Bot->>Bot: Format as Adaptive Card or text
    Bot-->>ABS: Response Activity
    ABS-->>Teams: Rendered response to employee
```

**Key Bot Framework components:**

#### a) `TeamsActivityHandler` (or `ActivityHandler`)

The main entry point for all incoming activities:

```python
from botbuilder.core import TurnContext
from botbuilder.core.teams import TeamsActivityHandler

class HRConciergeBot(TeamsActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        user_message = turn_context.activity.text
        
        # Forward to Azure AI Foundry agent
        agent_response = await self.run_foundry_agent(user_message, turn_context)
        
        # Send response back through Bot Framework
        await turn_context.send_activity(agent_response)
```

#### b) `BotFrameworkAdapter`

Handles HTTP layer, token validation, and channel communication:

```python
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication

adapter = CloudAdapter(ConfigurationBotFrameworkAuthentication(config))
```

#### c) Conversation State Management

Maintains thread IDs and conversation context across turns:

```python
from botbuilder.core import ConversationState, MemoryStorage

storage = MemoryStorage()  # Use CosmosDB/Blob for production
conversation_state = ConversationState(storage)
```

#### d) Adaptive Cards (Response Rendering)

Rich card UI for structured responses in Teams:

```json
{
  "type": "AdaptiveCard",
  "body": [
    {"type": "TextBlock", "text": "Legal Name Change", "weight": "Bolder", "size": "Medium"},
    {"type": "TextBlock", "text": "This is a Tier 2 (Complex) change requiring documentation.", "wrap": true},
    {"type": "FactSet", "facts": [
      {"title": "Required Docs", "value": "Marriage certificate or court order"},
      {"title": "Timeline", "value": "3-5 business days"},
      {"title": "Process", "value": "HR Service Center review"}
    ]}
  ],
  "actions": [
    {"type": "Action.OpenUrl", "title": "Open Workday HR Service Center", "url": "https://workday-simulator.../hr-service-center/complex-changes"}
  ]
}
```

---

### 4. Azure AI Foundry — The Custom AI Engine

This is the **brain** of the Custom Engine Agent. Azure AI Foundry hosts the native prompt agent with its model, instructions, and tools.

```mermaid
graph TB
    subgraph "Azure AI Foundry Project: hr-concierge-project"
        subgraph "Agent Configuration"
            INST[System Instructions<br/>HR domain rules, routing logic,<br/>tone guidelines, SLA info]
            MODEL[gpt-5.4-mini<br/>DataZoneStandard deployment<br/>Multi-region, auto-scaling]
        end
        
        subgraph "Function Tools"
            FT1[get_change_type_guidance<br/>→ Determines ESS vs Complex<br/>→ Returns docs, timeline, link]
            FT2[screen_grievance<br/>→ Determines ERLR vs GOOS<br/>→ Returns process & intake link]
            FT3[search_hr_knowledge_base<br/>→ RAG over HR policies<br/>→ Returns relevant excerpts]
        end
        
        subgraph "Knowledge Integration"
            CONN[Azure AI Search Connection<br/>hr-concierge-search]
            IDX[Index: hr-knowledge-base<br/>13 documents, semantic ranking]
        end
        
        subgraph "Thread Management"
            THR[Conversation Threads<br/>Per-user session context<br/>Multi-turn memory]
        end
    end

    INST --> MODEL
    MODEL --> FT1
    MODEL --> FT2
    MODEL --> FT3
    FT3 --> CONN
    CONN --> IDX

    style MODEL fill:#50e6ff,color:#000
    style IDX fill:#ffb900,color:#000
```

**Agent API interaction pattern (from the Bot):**

```
1. POST /threads                    → Create conversation thread
2. POST /threads/{id}/messages      → Add user message  
3. POST /threads/{id}/runs          → Execute agent reasoning
4. GET  /threads/{id}/runs/{id}     → Poll for completion
5. POST /threads/{id}/runs/{id}/submit_tool_outputs → Return tool results
6. GET  /threads/{id}/messages      → Retrieve agent response
```

**Why Azure AI Foundry as the engine:**
- Full control over system prompt (detailed HR routing logic)
- Native function tool support (no external orchestration needed)
- Built-in Azure AI Search integration for RAG
- Thread-based conversation management (multi-turn grievance screening)
- Content Safety applied at the model layer
- DataZoneStandard provides auto-scaling with no capacity planning

---

### 5. Azure AI Search — The Knowledge Layer

```mermaid
graph LR
    subgraph "Data Sources"
        SP[SharePoint Online<br/>5 HR Policy Documents]
        SN[ServiceNow<br/>8 KB Articles]
    end

    subgraph "Azure AI Search: hr-concierge-search"
        ING[Indexer Pipeline]
        IDX[Index: hr-knowledge-base<br/>13 documents]
        SEM[Semantic Ranker<br/>Understands HR intent]
        VEC[Vector Embeddings<br/>Hybrid search]
    end

    SP --> ING
    SN --> ING
    ING --> IDX
    IDX --> SEM
    IDX --> VEC

    subgraph "Query Flow"
        AGT[Agent asks:<br/>"name change policy"] --> SEM
        SEM --> RES[Top-K ranked results<br/>returned to agent context]
    end

    style IDX fill:#ffb900,color:#000
    style SEM fill:#ff6f00,color:#fff
```

**Indexed content:**

| Source | Documents | Content |
|--------|-----------|---------|
| SharePoint Online | 5 | ESS Guide, Complex Changes Policy, Grievance/ERLR Policy, GOOS Resolution Guide, HR Service Catalog |
| ServiceNow KB | 8 | Emergency Contact Steps, Legal Name Process, Direct Deposit Guide, Grievance Filing Steps, GOOS Request Guide, Preferred Name Steps, Passport/Visa Steps, Home Address Steps |

**Search capabilities:**
- **Semantic ranking** — understands natural language HR queries
- **Hybrid search** — combines keyword + vector similarity
- **Chunk-level retrieval** — returns most relevant passages, not entire documents

---

### 6. Microsoft Entra ID — Identity & Security

```mermaid
graph TB
    subgraph "Identity Flow"
        EMP[Employee<br/>VanceD@contoso.com] -->|SSO via M365| TEAMS[Microsoft Teams]
        TEAMS -->|Token exchange| BOT[Bot Service<br/>validates identity]
        BOT -->|Managed Identity| FOUNDRY[Azure AI Foundry<br/>agent execution]
        FOUNDRY -->|RBAC| SEARCH[Azure AI Search<br/>query index]
    end

    subgraph "App Registrations"
        APP1[Bot App Registration<br/>Client ID + Secret<br/>Teams channel permissions]
        APP2[AI Services Identity<br/>Managed Identity<br/>Cognitive Services User role]
    end

    subgraph "RBAC Assignments"
        R1[Azure AI Developer → Agent CRUD]
        R2[Cognitive Services User → Agent invocation]
        R3[Search Index Data Reader → Knowledge queries]
    end

    style EMP fill:#0078d4,color:#fff
```

**Security model:**
- Employee authenticates via existing M365 credentials (SSO)
- Bot validates incoming tokens using Bot Framework authentication
- Bot-to-Foundry calls use Managed Identity (no secrets in code)
- Foundry-to-Search uses connection-based RBAC
- All data stays within the Azure tenant boundary

---

### 7. Function Tools — The Action Layer

The agent has two primary function tools that drive its HR workflow logic:

#### `get_change_type_guidance`

```mermaid
flowchart TD
    A[Agent receives:<br/>"I need to change my legal name"] --> B[LLM determines tool call needed]
    B --> C[Tool: get_change_type_guidance<br/>change_type = "legal_name"]
    C --> D{Routing Logic}
    D -->|ESS types| E[Return: Tier 1<br/>No docs, immediate<br/>ESS deep link]
    D -->|Complex types| F[Return: Tier 2<br/>Docs required, 3-5 days<br/>HR Service Center link]
    F --> G[Agent formats response:<br/>"You'll need a marriage certificate...<br/>Here's the link to get started."]
```

**Input:** `change_type` enum (one of 10 HR change categories)  
**Output:** Tier classification, required documents, timeline, process steps, deep link URL

#### `screen_grievance`

```mermaid
flowchart TD
    A[Agent receives:<br/>"My manager is discriminating against me"] --> B[LLM asks clarifying questions]
    B --> C[Employee provides details]
    C --> D[Tool: screen_grievance<br/>involves_misconduct = true<br/>category = "discrimination"]
    D --> E{Routing Decision}
    E -->|Serious misconduct| F[ERLR Path<br/>Confidential investigation<br/>48hr case assignment]
    E -->|Workplace friction| G[GOOS Path<br/>Voluntary mediation<br/>1-2 week resolution]
    F --> H[Agent responds with empathy,<br/>confidentiality assurance,<br/>and ERLR intake link]
```

**Input:** concern summary, misconduct flag, category enum  
**Output:** Recommended path (ERLR/GOOS), process overview, timeline, protections, deep link

---

## Complete Request Flow — Step by Step

```mermaid
sequenceDiagram
    participant E as 👤 Employee<br/>in Teams
    participant C as M365 Copilot<br/>Agent Router
    participant B as Azure Bot Service
    participant F as Bot Framework App<br/>(App Service)
    participant A as Azure AI Foundry<br/>HR Concierge Agent
    participant L as gpt-5.4-mini
    participant T as Function Tools
    participant S as Azure AI Search

    Note over E,S: Employee asks about legal name change

    E->>C: "@HR Concierge I got married and need to change my last name"
    C->>C: Identifies target = Custom Engine Agent
    C->>B: Forward Activity (message)
    B->>B: Validate token, resolve endpoint
    B->>F: POST /api/messages<br/>{type:"message", text:"I got married..."}
    
    F->>F: Look up/create Foundry thread for this conversation
    F->>A: POST /threads/{tid}/messages (user message)
    F->>A: POST /threads/{tid}/runs (start agent)
    
    A->>L: System prompt + tools + user message
    L->>L: Reason: "This is a legal name change, call tool"
    L-->>A: requires_action: get_change_type_guidance("legal_name")
    
    A-->>F: Run status: requires_action
    F->>F: Execute tool locally or return canned response
    F->>A: POST /submit_tool_outputs<br/>{tier:"Complex", docs:"marriage cert", timeline:"3-5 days", link:"..."}
    
    A->>L: Incorporate tool output + generate response
    L-->>A: "Congratulations on your marriage! 🎉 For a legal name change..."
    A->>S: (Optional) RAG query for additional policy details
    S-->>A: Policy excerpt about required documents
    A-->>F: Final agent response
    
    F->>F: Format as Adaptive Card
    F-->>B: Response Activity (card + text)
    B-->>C: Deliver to channel
    C-->>E: Rendered response in Teams Copilot
    
    Note over E,S: Total latency: ~2-4 seconds
```

---

## App Manifest & Agent Declaration

To register as a Custom Engine Agent in M365 Copilot, the app requires a **Teams App Manifest** and an **Agent Declaration**.

### Teams App Manifest (`manifest.json`)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/teams/v1.19/MicrosoftTeams.schema.json",
  "manifestVersion": "1.19",
  "version": "1.0.0",
  "id": "{{BOT_APP_ID}}",
  "name": {
    "short": "HR Concierge",
    "full": "HR Concierge — AI HR Assistant"
  },
  "description": {
    "short": "Get help with personal data changes and workplace concerns",
    "full": "HR Concierge helps employees navigate personal data changes (ESS vs HR Service Center) and screens workplace grievances for proper routing (ERLR vs GOOS)."
  },
  "icons": {
    "color": "color.png",
    "outline": "outline.png"
  },
  "developer": {
    "name": "Contoso HR",
    "websiteUrl": "https://contoso.com/hr",
    "privacyUrl": "https://contoso.com/privacy",
    "termsOfUseUrl": "https://contoso.com/terms"
  },
  "bots": [
    {
      "botId": "{{BOT_APP_ID}}",
      "scopes": ["personal", "team", "groupChat"],
      "supportsFiles": false,
      "isNotificationOnly": false
    }
  ],
  "copilotAgents": {
    "customEngineAgents": [
      {
        "type": "customEngine",
        "id": "hrConcierge",
        "file": "agent.json"
      }
    ]
  },
  "validDomains": [
    "hr-bot.azurewebsites.net",
    "workday-simulator.grayplant-4b62ead6.eastus2.azurecontainerapps.io"
  ]
}
```

### Agent Declaration (`agent.json`)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/copilot/plugin/v1.0/schema.json",
  "name": "HR Concierge",
  "description": "AI-powered HR assistant for personal data changes and workplace grievance screening",
  "instructions": "You are HR Concierge, Contoso's AI HR assistant. Help employees with personal data changes and grievance screening. Use your tools to provide accurate routing and deep links.",
  "capabilities": [
    {
      "name": "conversation",
      "description": "Multi-turn conversations about HR processes, personal data changes, and workplace concerns"
    }
  ],
  "conversation_starters": [
    {"text": "I need to update my emergency contact"},
    {"text": "How do I change my legal name after marriage?"},
    {"text": "I want to report a workplace concern"},
    {"text": "What's the process for updating my bank details?"}
  ]
}
```

---

## Hosting Infrastructure

```mermaid
graph TB
    subgraph "Azure App Service (Bot Host)"
        APP[App Service Plan<br/>Linux / B1 or P1v2]
        WEB[Web App: hr-concierge-bot<br/>Python 3.11 + Bot Framework SDK]
        ENV[App Settings<br/>BOT_APP_ID, BOT_APP_SECRET<br/>FOUNDRY_ENDPOINT, AGENT_ID]
    end

    subgraph "Alternative: Azure Functions"
        FUNC[Function App<br/>Consumption or Premium plan<br/>HTTP Trigger → /api/messages]
    end

    subgraph "Azure AI Foundry (Engine)"
        AI[AI Services: hr-concierge-ai<br/>Hosts the agent + model]
    end

    subgraph "Azure Bot Service"
        BOT[Bot Channel Registration<br/>Messaging endpoint → App Service URL]
    end

    BOT --> APP
    BOT -.-> FUNC
    APP --> AI
    FUNC -.-> AI

    style APP fill:#0078d4,color:#fff
    style AI fill:#50e6ff,color:#000
    style BOT fill:#6f42c1,color:#fff
```

**Hosting options:**

| Option | Best For | Scaling | Cost |
|--------|----------|---------|------|
| **Azure App Service** | Always-on, predictable traffic | Manual/Auto scale rules | ~$55-200/mo |
| **Azure Functions (Consumption)** | Bursty traffic, cost-sensitive | Auto (0 to N instances) | Pay-per-execution |
| **Azure Functions (Premium)** | Low latency + scale | Pre-warmed instances | ~$150+/mo |
| **Azure Container Apps** | Containerized, microservices | KEDA-based auto-scale | ~$50-150/mo |

---

## Bot Framework Project Structure

```
hr-concierge-bot/
├── app.py                      # Entry point — HTTP server + adapter
├── bot.py                      # HRConciergeBot class (TeamsActivityHandler)
├── config.py                   # Environment config (App ID, secrets, endpoints)
├── foundry_client.py           # Azure AI Foundry agent interaction
├── cards/
│   ├── change_guidance.json    # Adaptive Card template for data changes
│   ├── grievance_result.json   # Adaptive Card template for grievance routing
│   └── welcome.json            # Welcome card for first interaction
├── manifest/
│   ├── manifest.json           # Teams app manifest
│   ├── agent.json              # Custom Engine Agent declaration
│   ├── color.png               # App icon (192x192)
│   └── outline.png             # App icon outline (32x32)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container build
└── infra/
    ├── main.bicep              # Infrastructure as Code
    ├── bot.bicep               # Bot Service + App Registration
    └── parameters.json         # Deployment parameters
```

---

## Key Dependencies

| Package | Purpose |
|---------|---------|
| `botbuilder-core` | Core Bot Framework abstractions |
| `botbuilder-integration-aiohttp` | HTTP adapter for receiving Activities |
| `botbuilder-dialogs` | (Optional) Multi-step dialog management |
| `azure-identity` | Managed Identity authentication to Foundry |
| `azure-ai-agents` | Azure AI Foundry agent SDK |
| `aiohttp` | Async HTTP server |
| `adaptivecards` | (Optional) Card template rendering |

---

## How M365 Copilot Discovers and Routes to the CEA

```mermaid
flowchart TD
    A[Admin uploads Teams App Package<br/>to M365 Admin Center] --> B[App Registration validated<br/>Bot endpoint verified]
    B --> C[Custom Engine Agent manifest parsed<br/>copilotAgents.customEngineAgents detected]
    C --> D[Agent appears in<br/>M365 Copilot agent gallery]
    D --> E[Employee selects HR Concierge<br/>or types @HR Concierge]
    E --> F{Is it a Custom Engine Agent?}
    F -->|Yes| G[M365 Copilot forwards<br/>entire message to Bot endpoint<br/>— NO Copilot orchestration —]
    F -->|No: Declarative| H[Copilot orchestrates<br/>using its own model]
    G --> I[Bot Framework App<br/>processes with AI Foundry]
    I --> J[Response sent back<br/>through Bot Channel]
    J --> K[Rendered in Teams Copilot UI]

    style F fill:#ff6f00,color:#fff
    style G fill:#0078d4,color:#fff
    style I fill:#50e6ff,color:#000
```

**Key insight:** For a Custom Engine Agent, M365 Copilot acts as a **pass-through**. It does not apply its own reasoning, grounding, or orchestration. The entire AI logic lives in your custom engine (Azure AI Foundry).

---

## Conversation State Management

```mermaid
stateDiagram-v2
    [*] --> NewConversation: Employee opens agent
    
    NewConversation --> ThreadCreated: Bot creates Foundry thread
    ThreadCreated --> WaitingForInput: Welcome message sent
    
    WaitingForInput --> ProcessingMessage: Employee sends message
    ProcessingMessage --> ToolExecution: Agent calls function tool
    ProcessingMessage --> RAGQuery: Agent searches knowledge base
    ProcessingMessage --> DirectResponse: Agent responds directly
    
    ToolExecution --> ResponseGenerated: Tool output incorporated
    RAGQuery --> ResponseGenerated: Search results grounded
    DirectResponse --> ResponseGenerated
    
    ResponseGenerated --> WaitingForInput: Response delivered
    
    WaitingForInput --> [*]: Conversation timeout (30 min)

    note right of ThreadCreated
        Thread ID stored in Bot conversation state
        Mapped: Teams conversation ID → Foundry thread ID
    end note
```

**State mapping:**
- Each Teams conversation maps to one Azure AI Foundry **thread**
- The Bot Framework maintains this mapping using `ConversationState`
- Foundry threads preserve full conversation history (multi-turn support)
- Thread context enables the agent to ask follow-up questions during grievance screening

---

## Security Architecture

```mermaid
graph TB
    subgraph "Layer 1: Channel Security"
        L1A[M365 Copilot authenticates employee via Entra ID]
        L1B[Bot Framework validates channel token]
        L1C[Only authorized tenants can invoke the bot]
    end

    subgraph "Layer 2: Bot-to-Engine Security"
        L2A[Managed Identity — no secrets in code]
        L2B[RBAC: Cognitive Services User role]
        L2C[VNet integration optional for network isolation]
    end

    subgraph "Layer 3: Data Security"
        L3A[Azure AI Search RBAC — no admin keys at runtime]
        L3B[Data stays in Azure tenant boundary]
        L3C[No customer data used for model training]
    end

    subgraph "Layer 4: AI Safety"
        L4A[Content Safety filters on input + output]
        L4B[Jailbreak detection]
        L4C[PII detection for grievance conversations]
        L4D[Grounding prevents hallucination of policy info]
    end

    L1A --> L2A --> L3A --> L4A

    style L1A fill:#0078d4,color:#fff
    style L4A fill:#e74c3c,color:#fff
```

---

## Monitoring & Observability

```mermaid
graph LR
    subgraph "Telemetry Sources"
        BOT[Bot Framework<br/>Activity logs, errors]
        FOUNDRY[AI Foundry<br/>Agent runs, tool calls, tokens]
        SEARCH[AI Search<br/>Query latency, result counts]
    end

    subgraph "Azure Monitor"
        AI_INS[Application Insights<br/>Bot telemetry]
        LOGS[Log Analytics<br/>Unified query]
        DASH[Workbooks Dashboard<br/>Operational view]
    end

    BOT --> AI_INS
    FOUNDRY --> LOGS
    SEARCH --> LOGS
    AI_INS --> DASH
    LOGS --> DASH

    subgraph "Key Metrics"
        M1[Avg response latency]
        M2[Tool call success rate]
        M3[Grievance → ERLR vs GOOS ratio]
        M4[Knowledge base hit rate]
        M5[Token consumption per conversation]
    end

    DASH --> M1 & M2 & M3 & M4 & M5

    style DASH fill:#0078d4,color:#fff
```

---

## Deployment Pipeline

```mermaid
flowchart LR
    A[Developer pushes code] --> B[GitHub Actions / Azure DevOps]
    B --> C{What changed?}
    
    C -->|Bot code| D[Build + Test<br/>Python unit tests]
    D --> E[Deploy to App Service<br/>Staging slot]
    E --> F[Smoke test bot endpoint]
    F --> G[Swap to production]
    
    C -->|Agent instructions| H[Update Foundry Agent<br/>via REST API]
    H --> I[Run test_agent.py<br/>Integration tests]
    
    C -->|Knowledge docs| J[Rebuild Search Index<br/>python create_search_index.py]
    J --> K[Validate document count]
    
    C -->|Manifest| L[Package Teams App<br/>Update in Admin Center]

    style G fill:#27ae60,color:#fff
```

---

## Summary: Why Custom Engine Agent for HR Concierge

| Requirement | Why CEA (not Declarative Agent) |
|-------------|-------------------------------|
| **Complex routing logic** | System prompt with detailed tier classification rules |
| **Custom function tools** | `get_change_type_guidance` and `screen_grievance` with enum-driven logic |
| **Multi-turn grievance screening** | Agent must ask clarifying questions before routing |
| **Domain-specific RAG** | Azure AI Search over SharePoint + ServiceNow (not just Graph) |
| **Controlled tone & empathy** | Full system prompt control for sensitive HR conversations |
| **Deep linking to Workday** | Tool outputs include specific portal URLs |
| **SLA communication** | Agent must cite exact timelines (immediate, 3-5 days, 48 hours) |
| **Confidentiality guarantees** | ERLR responses must include protection language |

---

## Architecture Decision Records

### ADR-1: Custom Engine Agent over Declarative Agent
**Decision:** Use Custom Engine Agent pattern  
**Rationale:** HR grievance screening requires multi-turn reasoning, custom tools, and full prompt control that Declarative Agents cannot provide.

### ADR-2: Azure AI Foundry Native Prompt Agent as Engine
**Decision:** Use Foundry native agent (not hosted container agent)  
**Rationale:** No custom code in the AI layer. Instructions + tools + search = full functionality. Zero infrastructure for the AI engine itself.

### ADR-3: Bot Framework as Communication Layer
**Decision:** Use Bot Framework SDK with Azure Bot Service  
**Rationale:** Required for M365 Copilot integration. Provides channel abstraction, authentication, and Adaptive Card rendering.

### ADR-4: Azure AI Search for Knowledge
**Decision:** Unified search index over SharePoint + ServiceNow  
**Rationale:** Employees shouldn't need to know which system holds the answer. Semantic ranking ensures the most relevant policy content surfaces.

### ADR-5: Function Tools over Code Interpreter
**Decision:** Use function tools with deterministic routing logic  
**Rationale:** HR routing must be predictable and auditable. Deterministic tool logic (enum → tier mapping) is safer than LLM-generated code for compliance-critical decisions.

---

## Comparison: Architecture Layers

| Layer | Technology | Role |
|-------|-----------|------|
| **Surface** | Microsoft 365 Copilot + Teams | Where employees interact |
| **Communication** | Azure Bot Service + Bot Framework SDK | Message routing & auth |
| **Application** | Python Bot (App Service / Functions) | Orchestration glue code |
| **AI Engine** | Azure AI Foundry (Native Prompt Agent) | Reasoning, tool calling, RAG |
| **Model** | gpt-5.4-mini (DataZoneStandard) | Language understanding & generation |
| **Knowledge** | Azure AI Search (Semantic) | Policy document retrieval |
| **Data Sources** | SharePoint Online + ServiceNow | Authoritative HR content |
| **Actions** | Workday deep links | Employee self-service portals |
| **Identity** | Microsoft Entra ID | SSO, RBAC, token validation |
| **Safety** | Azure Content Safety | Input/output filtering |
| **Observability** | Azure Monitor + App Insights | Telemetry, tracing, dashboards |

---

## Appendix: Private Network (BYO VNet) Deployment

### Overview

In regulated industries (finance, healthcare, government), organizations require that **all AI workloads run inside a private virtual network** with no public internet exposure. This section describes how the Custom Engine Agent architecture changes when:

- **Azure AI Foundry** is deployed with network isolation (BYO VNet / managed VNet)
- **Bot Framework App** (App Service) is behind a private endpoint
- **Azure AI Search** has public access disabled
- **M365 Copilot** (a Microsoft-managed SaaS service) must still reach the bot

---

### Private Network Architecture

```mermaid
graph TB
    subgraph "Microsoft 365 Cloud (Microsoft-managed)"
        COP[M365 Copilot<br/>Agent Router]
        ABS[Azure Bot Service<br/>Bot Channel Registration<br/>— always public-facing —]
    end

    subgraph "Customer Azure Subscription"
        subgraph "VNet: vnet-hr-concierge (10.0.0.0/16)"
            subgraph "Subnet: snet-bot (10.0.1.0/24)"
                APP[App Service: hr-concierge-bot<br/>VNet-integrated<br/>Private Endpoint inbound]
            end

            subgraph "Subnet: snet-ai (10.0.2.0/24)"
                PE_AI[Private Endpoint<br/>Microsoft.CognitiveServices<br/>hr-concierge-ai]
                AI[Azure AI Foundry<br/>hr-concierge-ai<br/>Public access: DISABLED]
            end

            subgraph "Subnet: snet-search (10.0.3.0/24)"
                PE_SR[Private Endpoint<br/>Microsoft.Search<br/>hr-concierge-search]
                SR[Azure AI Search<br/>hr-concierge-search<br/>Public access: DISABLED]
            end

            subgraph "Subnet: snet-pe (10.0.4.0/24)"
                PE_BOT[Private Endpoint<br/>Microsoft.Web/sites<br/>hr-concierge-bot]
            end

            DNS[Azure Private DNS Zones<br/>privatelink.cognitiveservices.azure.com<br/>privatelink.search.windows.net<br/>privatelink.azurewebsites.net]
        end

        subgraph "Network Security"
            NSG[Network Security Groups<br/>Restrict ingress/egress per subnet]
            FW[Azure Firewall or NVA<br/>— optional for egress control —]
        end
    end

    COP -->|"Public internet"| ABS
    ABS -->|"Calls bot messaging endpoint<br/>via App Service public hostname<br/>— OR via Service Tag routing —"| APP
    APP -->|"Private endpoint<br/>10.0.2.x"| PE_AI
    PE_AI --> AI
    APP -->|"Private endpoint<br/>10.0.3.x"| PE_SR
    PE_SR --> SR

    DNS -.-> PE_AI
    DNS -.-> PE_SR
    DNS -.-> PE_BOT
    NSG -.-> APP

    style COP fill:#6f42c1,color:#fff
    style ABS fill:#6f42c1,color:#fff
    style APP fill:#0078d4,color:#fff
    style AI fill:#50e6ff,color:#000
    style SR fill:#ffb900,color:#000
    style DNS fill:#4a4a4a,color:#fff
```

---

### The Core Challenge: M365 Copilot → Private Bot

M365 Copilot and Azure Bot Service are **Microsoft-managed SaaS services** that operate on the public internet. They cannot be placed inside your VNet. This creates a challenge:

> **How does a public-facing SaaS service (Bot Service) reach a bot that is inside a private network?**

#### Solution Options

```mermaid
flowchart TD
    A[M365 Copilot sends message<br/>to Azure Bot Service] --> B{How does Bot Service<br/>reach your bot?}
    
    B -->|Option 1| C[App Service with<br/>Access Restrictions<br/>— Recommended —]
    B -->|Option 2| D[Azure Front Door<br/>+ Private Link Origin]
    B -->|Option 3| E[API Management<br/>in VNet]
    
    C --> C1["• App Service VNet-integrated (outbound)<br/>• Public hostname still active<br/>• Access Restrictions: allow only<br/>  AzureBotService service tag<br/>• All other inbound blocked"]
    
    D --> D1["• Front Door receives from Bot Service<br/>• Private Link to App Service origin<br/>• App Service fully private<br/>• WAF on Front Door (bonus)"]
    
    E --> E1["• APIM in internal VNet mode<br/>• External gateway receives Bot traffic<br/>• Forwards to private App Service<br/>• Rate limiting, JWT validation"]

    style C fill:#27ae60,color:#fff
    style D fill:#0078d4,color:#fff
    style E fill:#f39c12,color:#000
```

---

### Option 1 (Recommended): App Service with Access Restrictions + VNet Integration

This is the simplest and most commonly used pattern.

```mermaid
graph LR
    subgraph "Public Internet"
        BOT_SVC[Azure Bot Service<br/>IP ranges: AzureBotService tag]
    end

    subgraph "App Service: hr-concierge-bot"
        ACL[Access Restrictions<br/>ALLOW: AzureBotService service tag<br/>DENY: all other]
        VNET_INT[VNet Integration<br/>Outbound → snet-bot]
    end

    subgraph "Private VNet"
        AI_PE[AI Foundry<br/>Private Endpoint]
        SR_PE[AI Search<br/>Private Endpoint]
    end

    BOT_SVC -->|"Allowed by<br/>service tag"| ACL
    ACL --> VNET_INT
    VNET_INT -->|"10.0.2.x"| AI_PE
    VNET_INT -->|"10.0.3.x"| SR_PE

    style ACL fill:#27ae60,color:#fff
    style VNET_INT fill:#0078d4,color:#fff
```

**How it works:**
1. App Service retains a public hostname (`hr-concierge-bot.azurewebsites.net`)
2. **Access Restrictions** are configured to allow inbound traffic **only** from the `AzureBotService` service tag
3. All other public inbound traffic is denied (no one else can reach the bot)
4. App Service has **VNet Integration** for outbound — all calls to Foundry and Search go through private endpoints
5. Azure AI Foundry and Search have **public network access disabled** — only reachable via private endpoints

**Configuration:**

```bash
# Enable VNet Integration (outbound)
az webapp vnet-integration add \
  --resource-group rg-hr-concierge \
  --name hr-concierge-bot \
  --vnet vnet-hr-concierge \
  --subnet snet-bot

# Add Access Restriction — allow only Bot Service
az webapp config access-restriction add \
  --resource-group rg-hr-concierge \
  --name hr-concierge-bot \
  --priority 100 \
  --service-tag AzureBotService \
  --action Allow

# Deny all other traffic (default deny)
az webapp config access-restriction set \
  --resource-group rg-hr-concierge \
  --name hr-concierge-bot \
  --default-action Deny
```

---

### Option 2: Azure Front Door + Private Link Origin

For organizations requiring the App Service to have **no public endpoint at all**.

```mermaid
graph LR
    subgraph "Public"
        BOT_SVC[Azure Bot Service]
        AFD[Azure Front Door Premium<br/>WAF policy applied]
    end

    subgraph "Private VNet"
        APP[App Service<br/>Public access: DISABLED<br/>Private Endpoint only]
        AI_PE[AI Foundry PE]
        SR_PE[AI Search PE]
    end

    BOT_SVC -->|"Bot messaging endpoint =<br/>Front Door custom domain"| AFD
    AFD -->|"Private Link origin<br/>to App Service"| APP
    APP --> AI_PE
    APP --> SR_PE

    style AFD fill:#6f42c1,color:#fff
    style APP fill:#0078d4,color:#fff
```

**How it works:**
1. App Service public access is **completely disabled** (private endpoint only)
2. Azure Front Door Premium connects to App Service via **Private Link origin**
3. Bot Channel Registration messaging endpoint is set to the Front Door URL
4. Front Door applies WAF rules (bot protection, rate limiting)
5. Bot Service calls Front Door → Front Door reaches App Service over private backbone

**Trade-offs:**
- ✅ App Service has zero public exposure
- ✅ WAF provides additional protection layer
- ❌ Requires Azure Front Door Premium (higher cost)
- ❌ Additional DNS/certificate management

---

### Option 3: API Management (Internal VNet Mode)

For enterprises with an existing APIM investment and strict API governance requirements.

```mermaid
graph LR
    subgraph "Public"
        BOT_SVC[Azure Bot Service]
        APIM_GW[APIM External Gateway<br/>api.contoso.com]
    end

    subgraph "Private VNet"
        APIM_INT[APIM Internal<br/>JWT validation, rate limiting,<br/>request transformation]
        APP[App Service<br/>Private Endpoint]
        AI_PE[AI Foundry PE]
    end

    BOT_SVC --> APIM_GW
    APIM_GW --> APIM_INT
    APIM_INT -->|"Private"| APP
    APP --> AI_PE

    style APIM_GW fill:#f39c12,color:#000
    style APP fill:#0078d4,color:#fff
```

---

### Private Endpoint Configuration for AI Foundry

When Azure AI Foundry is deployed with BYO network, the agent API is only accessible via private endpoint:

```mermaid
graph TB
    subgraph "Azure AI Foundry — Network Isolation"
        AI_PUB["Public endpoint: DISABLED<br/>hr-concierge-ai.cognitiveservices.azure.com<br/>→ returns 403"]
        AI_PE["Private Endpoint<br/>hr-concierge-ai.privatelink.cognitiveservices.azure.com<br/>→ resolves to 10.0.2.4"]
        AI_AGENT[Agent: hr-concierge<br/>Threads, Runs, Messages API]
    end

    subgraph "Private DNS Zone"
        PDNS["privatelink.cognitiveservices.azure.com<br/>A record: hr-concierge-ai → 10.0.2.4"]
    end

    subgraph "Bot App (VNet-integrated)"
        BOT[Bot code calls:<br/>https://hr-concierge-ai.cognitiveservices.azure.com/...<br/>DNS resolves → 10.0.2.4 via Private DNS]
    end

    BOT -->|"Resolves privately"| PDNS
    PDNS --> AI_PE
    AI_PE --> AI_AGENT

    style AI_PUB fill:#e74c3c,color:#fff
    style AI_PE fill:#27ae60,color:#fff
    style BOT fill:#0078d4,color:#fff
```

**Key points:**
- The SDK endpoint URL **stays the same** (`https://hr-concierge-ai.cognitiveservices.azure.com`)
- Azure Private DNS Zone ensures the hostname resolves to the private IP when called from within the VNet
- No code changes needed — only infrastructure configuration
- The Foundry project, agent, and model deployment all work identically over private endpoint

---

### Private AI Search Configuration

```bash
# Disable public access on AI Search
az search service update \
  --resource-group rg-hr-concierge \
  --name hr-concierge-search \
  --public-network-access disabled

# Create private endpoint for Search
az network private-endpoint create \
  --resource-group rg-hr-concierge \
  --name pe-hr-search \
  --vnet-name vnet-hr-concierge \
  --subnet snet-search \
  --private-connection-resource-id /subscriptions/{sub}/resourceGroups/rg-hr-concierge/providers/Microsoft.Search/searchServices/hr-concierge-search \
  --group-id searchService \
  --connection-name search-pe-connection

# Link Private DNS Zone
az network private-dns zone create \
  --resource-group rg-hr-concierge \
  --name privatelink.search.windows.net

az network private-dns link vnet create \
  --resource-group rg-hr-concierge \
  --zone-name privatelink.search.windows.net \
  --name search-dns-link \
  --virtual-network vnet-hr-concierge \
  --registration-enabled false
```

---

### Complete Private Network Data Flow

```mermaid
sequenceDiagram
    participant E as 👤 Employee<br/>(Teams)
    participant C as M365 Copilot<br/>(Public SaaS)
    participant B as Azure Bot Service<br/>(Public SaaS)
    participant F as App Service<br/>(VNet-integrated)
    participant A as AI Foundry<br/>(Private Endpoint)
    participant S as AI Search<br/>(Private Endpoint)

    Note over C,B: PUBLIC INTERNET
    Note over F,S: PRIVATE VNET (no public access)

    E->>C: "I need to change my name"
    C->>B: Route to Custom Engine Agent
    B->>F: POST /api/messages<br/>(allowed via AzureBotService service tag)
    
    Note over F: App Service resolves AI Foundry hostname<br/>via Private DNS → 10.0.2.4

    F->>A: POST /threads (via private endpoint 10.0.2.4)
    F->>A: POST /threads/{id}/messages
    F->>A: POST /threads/{id}/runs
    A->>A: LLM processing (inside Microsoft network)
    A-->>F: requires_action: tool call
    F->>F: Execute tool logic locally
    F->>A: Submit tool outputs (private endpoint)
    
    A->>S: RAG query (Foundry → Search via private backbone<br/>or via shared VNet if configured)
    S-->>A: Document chunks
    A-->>F: Final response (private endpoint)
    
    F-->>B: Response Activity
    B-->>C: Deliver to channel
    C-->>E: Rendered in Teams

    Note over F,S: ALL traffic between Bot, Foundry,<br/>and Search stays on private network
```

---

### Network Security Group Rules

```mermaid
graph TB
    subgraph "NSG: nsg-snet-bot"
        R1["Inbound ALLOW: AzureBotService → 443<br/>Inbound DENY: * → *<br/>Outbound ALLOW: VNet → VNet (10.0.0.0/16)<br/>Outbound ALLOW: AzureMonitor (for telemetry)<br/>Outbound DENY: Internet (optional)"]
    end

    subgraph "NSG: nsg-snet-ai"
        R2["Inbound ALLOW: snet-bot (10.0.1.0/24) → 443<br/>Inbound DENY: * → *<br/>Outbound: managed by service"]
    end

    subgraph "NSG: nsg-snet-search"
        R3["Inbound ALLOW: snet-ai (10.0.2.0/24) → 443<br/>Inbound ALLOW: snet-bot (10.0.1.0/24) → 443<br/>Inbound DENY: * → *"]
    end

    style R1 fill:#0078d4,color:#fff
    style R2 fill:#50e6ff,color:#000
    style R3 fill:#ffb900,color:#000
```

---

### Managed VNet (AI Foundry) vs BYO VNet

Azure AI Foundry supports two network isolation modes:

| Aspect | Managed VNet | BYO VNet (Customer-managed) |
|--------|-------------|---------------------------|
| **VNet ownership** | Microsoft creates & manages | Customer creates & manages |
| **Private endpoints** | Auto-provisioned in managed VNet | Customer creates in their VNet |
| **Outbound control** | Allow only approved destinations | Full NSG/Firewall control |
| **Complexity** | Low — mostly automated | High — customer manages networking |
| **Use case** | Standard isolation needs | Strict compliance, custom routing, hub-spoke topology |
| **AI Search connectivity** | Managed PE auto-created | Customer must configure PE + DNS |
| **Bot integration** | Bot needs PE into managed VNet (or public allowed list) | Bot VNet-integrated into same VNet or peered VNet |

**For this HR Concierge scenario (BYO VNet):**
- Customer manages `vnet-hr-concierge`
- All resources get private endpoints in customer-owned subnets
- Hub-spoke or flat VNet topology depending on enterprise standards
- Bot App Service uses VNet Integration to reach everything privately

---

### DNS Resolution Chain

```mermaid
flowchart LR
    A[Bot code calls:<br/>hr-concierge-ai.cognitiveservices.azure.com] --> B{DNS Resolution}
    B -->|"From public internet"| C["Public IP → 403 Forbidden<br/>(public access disabled)"]
    B -->|"From inside VNet"| D[Azure Private DNS Zone<br/>privatelink.cognitiveservices.azure.com]
    D --> E[CNAME → hr-concierge-ai.privatelink.cognitiveservices.azure.com]
    E --> F[A record → 10.0.2.4<br/>(Private Endpoint NIC)]
    F --> G[✅ Request reaches AI Foundry<br/>over private backbone]

    style C fill:#e74c3c,color:#fff
    style G fill:#27ae60,color:#fff
```

---

### Infrastructure as Code (Bicep)

```bicep
// Private Endpoint for AI Foundry
resource aiPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-11-01' = {
  name: 'pe-hr-concierge-ai'
  location: location
  properties: {
    subnet: {
      id: vnet::subnetAi.id
    }
    privateLinkServiceConnections: [
      {
        name: 'ai-pe-connection'
        properties: {
          privateLinkServiceId: aiServices.id
          groupIds: ['account']
        }
      }
    ]
  }
}

// Private DNS Zone for Cognitive Services
resource privateDnsZoneAi 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'privatelink.cognitiveservices.azure.com'
  location: 'global'
}

// Link DNS Zone to VNet
resource dnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: privateDnsZoneAi
  name: 'ai-dns-vnet-link'
  location: 'global'
  properties: {
    virtualNetwork: {
      id: vnet.id
    }
    registrationEnabled: false
  }
}

// App Service VNet Integration
resource appServiceVnetIntegration 'Microsoft.Web/sites/networkConfig@2023-12-01' = {
  parent: botAppService
  name: 'virtualNetwork'
  properties: {
    subnetResourceId: vnet::subnetBot.id
    swiftSupported: true
  }
}

// App Service Access Restriction — only Bot Service
resource appServiceConfig 'Microsoft.Web/sites/config@2023-12-01' = {
  parent: botAppService
  name: 'web'
  properties: {
    ipSecurityRestrictions: [
      {
        name: 'AllowBotService'
        priority: 100
        action: 'Allow'
        tag: 'ServiceTag'
        ipAddress: 'AzureBotService'
      }
      {
        name: 'DenyAll'
        priority: 200
        action: 'Deny'
        ipAddress: 'Any'
      }
    ]
  }
}
```

---

### What Changes in the Bot Code?

**Nothing.** That is the key benefit of private endpoints with Azure Private DNS:

| Concern | Change Required? | Notes |
|---------|-----------------|-------|
| Foundry SDK endpoint URL | ❌ No | Same hostname, DNS resolves privately |
| Authentication | ❌ No | Managed Identity works the same |
| Agent API calls | ❌ No | Threads/Runs/Messages API unchanged |
| Search queries | ❌ No | Same endpoint, private resolution |
| Bot Framework protocol | ❌ No | Bot Service calls your public/restricted hostname |
| Adaptive Cards | ❌ No | Rendered client-side in Teams |

The only changes are **infrastructure** (VNet, Private Endpoints, DNS Zones, NSGs, Access Restrictions). Application code is network-topology agnostic.

---

### Checklist: Private Deployment

- [ ] Create VNet with subnets for Bot, AI, Search, and Private Endpoints
- [ ] Deploy Private Endpoint for Azure AI Foundry (Cognitive Services)
- [ ] Deploy Private Endpoint for Azure AI Search
- [ ] Create Private DNS Zones and link to VNet
- [ ] Disable public network access on AI Foundry
- [ ] Disable public network access on AI Search
- [ ] Enable VNet Integration on App Service (outbound)
- [ ] Configure Access Restrictions on App Service (allow `AzureBotService` only)
- [ ] Update App Service DNS settings: `WEBSITE_DNS_SERVER=168.63.129.16` (Azure DNS)
- [ ] Enable `WEBSITE_VNET_ROUTE_ALL=1` to route all outbound through VNet
- [ ] Verify NSG rules allow subnet-to-subnet traffic on port 443
- [ ] Test end-to-end: Teams → Bot → Foundry → Search (all private)

---

*Updated: July 20, 2026*  
*Agent: HR Concierge v3.0.0*  
*Pattern: Custom Engine Agent (M365 Copilot → Bot Framework → Azure AI Foundry)*  
*Network: BYO VNet with Private Endpoints*
