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

*Document created: July 20, 2026*  
*Agent: HR Concierge v3.0.0*  
*Pattern: Custom Engine Agent (M365 Copilot → Bot Framework → Azure AI Foundry)*
