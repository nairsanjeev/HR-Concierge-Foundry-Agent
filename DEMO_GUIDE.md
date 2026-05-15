# HR Concierge Agent - Demo & Test Guide

## Overview

**Agent**: HR Concierge  
**Agent ID**: `asst_PRduntIyCvJgvkvcc7y4bqSB`  
**Project Endpoint**: `https://hr-concierge-ai.services.ai.azure.com/api/projects/hr-concierge-project`  
**Model**: gpt-54-mini (DataZoneStandard)  
**Foundry Portal**: https://ai.azure.com  
**Workday Simulator**: https://workday-simulator.grayplant-4b62ead6.eastus2.azurecontainerapps.io/

---

## How to Access

### Option 1: Foundry Playground
1. Go to https://ai.azure.com
2. Sign in as `VanceD@M365CPI47937014.OnMicrosoft.com`
3. Navigate to **hr-concierge-ai** → **hr-concierge-project**
4. Open **Agents** → select **hr-concierge**
5. Use the chat playground to test prompts below

### Option 2: Run Integration Tests
```powershell
cd C:\HRAgentService
$env:AZURE_SEARCH_ADMIN_KEY = "<your-search-admin-key>"
.\.\.venv\Scripts\python.exe test_agent.py
```

### Option 3: Run Search-Grounded Agent Test
```powershell
cd C:\HRAgentService
$env:AZURE_SEARCH_ADMIN_KEY = "<your-search-admin-key>"
.\test_search_agent.ps1
```

---

## Demo Scenarios

### Scenario 1: Personal Data Changes — ESS (Self-Service)

These prompts should route to **ESS (Tier 1)** — immediate, no approval, no documentation.

| # | Prompt | Expected Behavior |
|---|--------|-------------------|
| 1.1 | "I need to update my emergency contact information." | Routes to ESS. Provides steps and deep link. No docs needed. |
| 1.2 | "How do I change my home address? I just moved." | Routes to ESS. Mentions immediate effect. May note tax implications if state change. |
| 1.3 | "I'd like to be called Alex instead of Alexander. How do I update that?" | Routes to ESS preferred name. Clarifies this is display name only, not legal name. |
| 1.4 | "I recently got married and want to update my marital status." | Routes to ESS personal info. Marital status = ESS (immediate). Should NOT confuse with legal name change. |
| 1.5 | "Can I update my pronouns in the system?" | Routes to ESS personal info. Immediate, no approval. |

**Key validation points:**
- Agent says "no approval required" or "immediate"
- Agent provides deep link: `https://workday-simulator.grayplant-4b62ead6.eastus2.azurecontainerapps.io/ess/personal-data`
- Agent does NOT ask for documentation

---

### Scenario 2: Personal Data Changes — Complex (HR Service Center)

These prompts should route to **HR Service Center (Tier 2)** — documentation required, 3-5 day review.

| # | Prompt | Expected Behavior |
|---|--------|-------------------|
| 2.1 | "I just got married and need to change my legal last name." | Routes to Complex. Asks for marriage certificate. 3-5 days. |
| 2.2 | "My passport expired and I got a new one. How do I update it?" | Routes to Complex. Needs copy of new passport. |
| 2.3 | "I need to change my direct deposit to a new bank account." | Routes to Complex. Requires voided check or bank letter. |
| 2.4 | "I got a new SSN card after a typo was corrected. How do I update?" | Routes to Complex (Government ID). Needs new SSN card. |
| 2.5 | "I want to update my professional photo in the system." | Routes to Complex. Photo must meet company guidelines. |
| 2.6 | "I just passed my PMP certification. Where do I add it?" | Routes to Complex (Licenses). Needs copy of certificate. |

**Key validation points:**
- Agent mentions "documentation required"
- Agent specifies the exact document needed (certificate, voided check, etc.)
- Agent mentions "3-5 business days" timeline
- Agent provides deep link: `https://workday-simulator.grayplant-4b62ead6.eastus2.azurecontainerapps.io/hr-service-center/complex-changes`

---

### Scenario 3: Ambiguous Personal Data — Agent Should Clarify

These test the agent's ability to ask clarifying questions.

| # | Prompt | Expected Behavior |
|---|--------|-------------------|
| 3.1 | "I need to change my name." | Agent should ASK: "Do you mean your legal name (requires docs) or your preferred/display name (self-service)?" |
| 3.2 | "I need to update my information after getting married." | Agent should clarify what specifically: legal name? marital status? address? emergency contact? (Could be multiple changes) |
| 3.3 | "How do I update my bank details and address?" | Agent should handle both: bank = Complex, address = ESS. Explains each separately. |
| 3.4 | "I'm moving to another country next month." | Agent should flag this as more complex — recommend contacting HR Global Mobility BEFORE the move, plus address change via ESS. |

**Key validation points:**
- Agent asks clarifying questions instead of assuming
- Agent correctly differentiates ESS vs Complex for multi-part requests
- Agent provides guidance for edge cases

---

### Scenario 4: Grievance Screening — ERLR (Formal)

These should route to **ERLR** — formal investigation, confidential, 48-hour case assignment.

| # | Prompt | Expected Behavior |
|---|--------|-------------------|
| 4.1 | "My manager keeps making sexual comments. I want to file a complaint." | Routes to ERLR. Harassment. Mentions confidentiality. |
| 4.2 | "I was passed over for promotion because of my age. I'm 58 and they gave it to someone 10 years younger with less experience." | Routes to ERLR. Discrimination (age). |
| 4.3 | "I reported a safety issue last month and now my hours are being cut. I think it's retaliation." | Routes to ERLR. Retaliation. References whistleblower protection. |
| 4.4 | "A coworker threatened to 'make me pay' if I reported their behavior. I feel unsafe." | Routes to ERLR. Threats/violence. May mention Security (Ext. 9999) for immediate danger. |
| 4.5 | "I discovered my manager is submitting false expense reports. Who do I tell?" | Routes to ERLR. Ethical violation/fraud. |
| 4.6 | "I requested a standing desk for my back condition and my manager denied it without explanation." | Routes to ERLR. Accommodation violation (ADA). |
| 4.7 | "My team lead constantly belittles me in meetings, calls me stupid, and has isolated me from the group for months." | Routes to ERLR. Bullying/hostile work environment. |

**Key validation points:**
- Agent mentions "formal grievance" or "ERLR"
- Agent emphasizes CONFIDENTIALITY
- Agent mentions retaliation is PROHIBITED
- Agent provides deep link: `https://workday-simulator.grayplant-4b62ead6.eastus2.azurecontainerapps.io/erlr/intake`
- Agent mentions 48-hour case manager assignment
- Agent shows empathy (e.g., "I'm sorry you're dealing with this")
- Agent does NOT determine whether misconduct occurred

---

### Scenario 5: Grievance Screening — GOOS (Informal)

These should route to **GOOS** — voluntary mediation, no disciplinary action, 1-2 week resolution.

| # | Prompt | Expected Behavior |
|---|--------|-------------------|
| 5.1 | "My coworker plays music too loudly and won't use headphones." | Routes to GOOS. Workspace/noise issue. |
| 5.2 | "I feel left out of team lunches and social events. It's not about my race or anything, I just feel excluded." | Routes to GOOS. Social exclusion (not discrimination). |
| 5.3 | "My manager and I disagree about my work schedule flexibility." | Routes to GOOS. Manager disagreement / scheduling. |
| 5.4 | "Two people on my team are constantly arguing and it's bringing everyone down." | Routes to GOOS. Team dynamics / interpersonal conflict. |
| 5.5 | "I don't feel like my manager clearly communicates expectations." | Routes to GOOS. Unclear expectations / communication. |
| 5.6 | "I'm finding it hard to balance work and family since our return-to-office mandate." | Routes to GOOS. Work-life balance concern. |

**Key validation points:**
- Agent mentions "GOOS" or "Good Office Services" or "informal resolution"
- Agent mentions it's VOLUNTARY
- Agent mentions mediation/coaching/facilitation options
- Agent provides deep link: `https://workday-simulator.grayplant-4b62ead6.eastus2.azurecontainerapps.io/goos/request`
- Agent mentions 2-day coordinator contact
- Agent does NOT escalate unnecessarily

---

### Scenario 6: Boundary Cases — ERLR vs GOOS

These test the agent's screening judgment on borderline cases.

| # | Prompt | Expected Behavior |
|---|--------|-------------------|
| 6.1 | "My coworker keeps commenting on my weight. Is that harassment?" | Agent should explore further. If persistent/unwanted comments about a physical characteristic → leans ERLR. Should ask more questions. |
| 6.2 | "My manager yelled at me once in a meeting. Everyone heard it." | Borderline. Agent may ask: Was this a one-time outburst vs. pattern? Does it feel like bullying? May offer both paths. |
| 6.3 | "I think my coworker is stealing office supplies." | Minor ethical concern. Agent may suggest talking to manager first or GOOS. Not necessarily ERLR. |
| 6.4 | "I feel discriminated against because my manager gives all the good projects to his friends." | Agent should probe: Is this nepotism/favoritism (GOOS) or based on a protected characteristic (ERLR)? |
| 6.5 | "Someone keeps leaving passive-aggressive sticky notes on my desk." | Could be either. Agent should ask about content, frequency, and whether it's targeted at a protected characteristic. |

**Key validation points:**
- Agent asks follow-up questions on ambiguous cases
- Agent does not rush to categorize without understanding the situation
- Agent may offer BOTH options and let employee decide
- Agent explains the key distinction: "misconduct" → ERLR, "workplace friction" → GOOS

---

### Scenario 7: Out-of-Scope Requests

These test graceful handling of requests outside the agent's domain.

| # | Prompt | Expected Behavior |
|---|--------|-------------------|
| 7.1 | "What's the company holiday schedule this year?" | Politely redirects. Not in agent's scope. May suggest HR portal or hr-service@contoso.com. |
| 7.2 | "How do I enroll in dental benefits?" | Redirects to benefits team. May provide benefits deep link or Ext. 3333. |
| 7.3 | "I want to apply for an internal transfer to another department." | Out of scope. Redirects to careers/mobility team. |
| 7.4 | "Can you approve my vacation request?" | Out of scope. Agent should clarify it cannot take actions, only guide. Redirects to manager/leave system. |
| 7.5 | "What's the WiFi password in the office?" | Out of scope. IT helpdesk. |

**Key validation points:**
- Agent acknowledges the question politely
- Agent clearly states it can't help with that specific topic
- Agent provides a redirect (email, phone, or portal)

---

### Scenario 8: Multi-Turn Conversations

These test the agent's ability to hold context across a conversation.

**Conversation 8A: From ambiguous to specific**
```
User: "I need to make some changes to my personal info."
Agent: [Should ask what kind of changes]
User: "I want to update my address and also change my legal name."
Agent: [Should explain address = ESS (immediate), legal name = Complex (needs docs)]
User: "For the name change, I have a court order."
Agent: [Should confirm court order works, give steps for Complex change]
```

**Conversation 8B: Grievance escalation**
```
User: "I'm having trouble with a coworker."
Agent: [Should ask about the nature of the trouble]
User: "They keep making jokes about my accent."
Agent: [Should ask if this is based on national origin/ethnicity - leans ERLR]
User: "Yes, they mock the way I speak and others laugh."
Agent: [Should route to ERLR as discrimination/harassment, provide intake link]
```

**Conversation 8C: GOOS to ERLR escalation**
```
User: "My manager and I aren't getting along."
Agent: [Should ask about the nature - initially sounds GOOS]
User: "They told me if I report them for anything, they'll make sure I'm fired."
Agent: [Should immediately pivot to ERLR - this is now retaliation/threats]
```

---

### Scenario 9: Knowledge Base Search (RAG)

These prompts test the agent's ability to search the HR knowledge base for policy information.

| # | Prompt | Expected Behavior |
|---|--------|-------------------|
| 9.1 | "What is the ERLR investigation timeline? What happens after an investigation?" | Agent calls `search_hr_knowledge_base`. Responds with details from KB (10-30 days, findings, appeal process). |
| 9.2 | "What benefits does Contoso offer for parental leave?" | Agent searches KB. Returns policy details about parental leave from ServiceNow/SharePoint docs. |
| 9.3 | "Tell me about the employee referral bonus program." | Agent searches KB. Returns relevant policy info or states not found. |
| 9.4 | "What's the difference between short-term and long-term disability?" | Agent searches KB for disability policy information. |
| 9.5 | "How do I request a reasonable accommodation?" | May route to ERLR (if discrimination) or search KB for accommodation process docs. |

**Key validation points:**
- Agent calls `search_hr_knowledge_base` function tool (visible in run steps)
- Response includes specific details from indexed documents, not just generic knowledge
- Agent may cite document sources
- Falls back gracefully if no matching documents found

---

## Function Tool Behavior

The agent uses three function tools. During the demo, you'll see these being invoked:

### `get_change_type_guidance`
- **Input**: `change_type` (enum)
- **Output**: tier, documentation requirements, timeline, deep link, steps
- **Triggers on**: Any clear personal data change request

### `screen_grievance`
- **Input**: `concern_summary`, `involves_misconduct` (bool), `concern_category` (enum)
- **Output**: recommended path (ERLR/GOOS), reason, deep link, process, protections/key points
- **Triggers on**: Any workplace concern or grievance-related question

### `search_hr_knowledge_base`
- **Input**: `query` (string), `top_results` (integer, optional, default 3)
- **Output**: Relevant HR policy documents, procedures, and FAQs from the knowledge base
- **Triggers on**: Questions about HR policies, benefits, or procedures not directly covered in the agent's instructions
- **Backend**: Calls Azure AI Search (index: `hr-knowledge-base`, 13 documents from SharePoint + ServiceNow)

---

## Key Deep Links Reference

All deep links route to the live Workday Simulator deployed on Azure Container Apps:

| Destination | URL |
|-------------|-----|
| Home (Portal) | https://workday-simulator.grayplant-4b62ead6.eastus2.azurecontainerapps.io/ |
| ESS Portal | https://workday-simulator.grayplant-4b62ead6.eastus2.azurecontainerapps.io/ess/personal-data |
| Complex Changes | https://workday-simulator.grayplant-4b62ead6.eastus2.azurecontainerapps.io/hr-service-center/complex-changes |
| ERLR Intake | https://workday-simulator.grayplant-4b62ead6.eastus2.azurecontainerapps.io/erlr/intake |
| GOOS Request | https://workday-simulator.grayplant-4b62ead6.eastus2.azurecontainerapps.io/goos/request |

---

## SLA Quick Reference

| Service | SLA |
|---------|-----|
| ESS Changes | Immediate |
| Complex Changes (HR Review) | 3-5 business days |
| ERLR Case Manager Assignment | 48 hours |
| ERLR Investigation | 10-30 calendar days |
| GOOS Coordinator Contact | 2 business days |
| GOOS Resolution | 1-2 weeks |

---

## Workday Simulator (Live Deployment)

**Public URL**: https://workday-simulator.grayplant-4b62ead6.eastus2.azurecontainerapps.io/

The Workday simulator is deployed as an Azure Container App with public ingress. Deep links from the agent resolve directly to the correct page.

### Infrastructure
| Resource | Value |
|----------|-------|
| ACR | `hrconciergeacr.azurecr.io` |
| Image | `hrconciergeacr.azurecr.io/workday-simulator:v1` |
| Container Apps Environment | `hr-concierge-env` (eastus2) |
| Container App | `workday-simulator` |
| Ingress | External, port 80 |
| Scale | 0-1 replicas (cold start ~5s) |

### Pages
- **Home**: Quick links to all sections
- **ESS (Self-Service)**: Emergency contact, address, preferred name, personal info forms
- **HR Service Center (Complex)**: Legal name, passport, govt ID, licenses, bank details, photo change
- **ERLR Intake**: Full formal grievance filing form with incident details, witnesses, evidence upload
- **GOOS Request**: Informal conflict resolution form with situation description and desired outcomes

### Deep Link Routing
Nginx rewrites URL paths to the SPA with query params. Client-side JavaScript reads `window.location.pathname` to show the correct page. Example:
- Request: `/erlr/intake` → nginx serves `index.html?page=erlr` → JS shows ERLR page

### Rebuild & Redeploy
```powershell
cd C:\HRAgentService\workday-simulator
az acr build --registry hrconciergeacr --image workday-simulator:v2 .
az containerapp update --name workday-simulator --resource-group rg-hr-concierge --image hrconciergeacr.azurecr.io/workday-simulator:v2
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure AI Foundry                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  hr-concierge-project                                │  │
│  │                                                      │  │
│  │  ┌────────────────────┐    ┌─────────────────────┐  │  │
│  │  │  HR Concierge Agent│    │  gpt-5.4-mini       │  │  │
│  │  │  (Native/Prompt)   │───▶│  (DataZoneStandard) │  │  │
│  │  └────────┬───────────┘    └─────────────────────┘  │  │
│  │           │                                          │  │
│  │     ┌─────┴──────┐                                  │  │
│  │     │ Function    │                                  │  │
│  │     │ Tools (x3)  │                                  │  │
│  │     └─────┬───────┘                                  │  │
│  └───────────┼──────────────────────────────────────────┘  │
│              │                                              │
└──────────────┼──────────────────────────────────────────────┘
               │
    ┌──────────┴──────────────────────┐
    │                │                │
    ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
│get_change_   │ │screen_       │ │search_hr_        │
│type_guidance │ │grievance     │ │knowledge_base    │
└──────┬───────┘ └──────┬───────┘ └────────┬─────────┘
       │                │                   │
       ▼                ▼                   ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
│ESS / Complex │ │ERLR / GOOS   │ │Azure AI Search   │
│Routing Logic │ │Routing Logic │ │(hr-knowledge-base│
└──────────────┘ └──────────────┘ │ 13 documents)    │
                                  └──────────────────┘

Supporting Infrastructure:
┌──────────────────────────────────────────┐
│ Azure AI Search (hr-concierge-search)    │
│ Index: hr-knowledge-base (13 documents)  │
│ - SharePoint HR policies (5 docs)        │
│ - ServiceNow KB articles (8 docs)        │
│ Semantic config: hr-semantic-config       │
│ Connection: hr-search-connection (API key)│
└──────────────────────────────────────────┘
┌──────────────────────────────────────────┐
│ Workday Simulator (Azure Container Apps) │
│ URL: workday-simulator.grayplant-4b62ead │
│      6.eastus2.azurecontainerapps.io     │
│ Pages: Home, ESS, Complex, ERLR, GOOS   │
│ Routing: nginx rewrite → SPA deep links  │
└──────────────────────────────────────────┘
┌──────────────────────────────────────────┐
│ External Systems (Data Sources)          │
│ - SharePoint: HR Docs library            │
│ - ServiceNow: KB articles (copilota2a)   │
└──────────────────────────────────────────┘
```

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| 401 Unauthorized | Re-run `az login --tenant M365CPI47937014.OnMicrosoft.com` |
| Token expired | Get fresh token: `az account get-access-token --resource https://ai.azure.com` |
| Agent not responding | Verify agent exists: check `list_agents` endpoint |
| Function tool timeout | Check that tool outputs are being submitted within 60s |
| RBAC denied | VanceD needs "Azure AI Developer" role on hr-concierge-ai resource |
| Search tool returns empty | Verify `AZURE_SEARCH_ADMIN_KEY` env var is set; check index has docs: `az search query-key list` |
| Workday Simulator timeout | Cold start from 0 replicas takes ~5s. First request may be slow. |
| Simulator shows wrong page | Check nginx.conf routes match the URL path. Verify JS path matching in index.html. |
| Container App 404 | Verify container is running: `az containerapp show --name workday-simulator --resource-group rg-hr-concierge --query "properties.runningStatus"` |
| Deep links in agent response still show contoso.com | Re-run `create_agent.py` or update agent instructions via REST API |

---

## Environment Variables

For running tests locally, set these:

```powershell
$env:AZURE_SEARCH_ADMIN_KEY = "<your-search-admin-key>"
```

Get the key:
```powershell
az search admin-key show --resource-group rg-hr-concierge --service-name hr-concierge-search --query primaryKey -o tsv
```
