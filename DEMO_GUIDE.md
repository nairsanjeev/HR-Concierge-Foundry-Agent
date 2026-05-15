# HR Concierge Agent - Demo & Test Guide

## Overview

**Agent**: HR Concierge  
**Agent ID**: `asst_AR1WuyJx8uslI2GOgZjA4hAJ`  
**Project Endpoint**: `https://hr-concierge-ai.services.ai.azure.com/api/projects/hr-concierge-project`  
**Model**: gpt-5.4-mini (DataZoneStandard)  
**Foundry Portal**: https://ai.azure.com

---

## How to Access

### Option 1: Foundry Playground
1. Go to https://ai.azure.com
2. Sign in as `VanceD@M365CPI47937014.OnMicrosoft.com`
3. Navigate to **hr-concierge-ai** → **hr-concierge-project**
4. Open **Agents** → select **hr-concierge**
5. Use the chat playground to test prompts below

### Option 2: Run Test Script
```powershell
cd C:\HRAgentService
.\.venv\Scripts\python.exe test_agent.py
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
- Agent provides deep link: `https://workday.contoso.com/ess/personal-data`
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
- Agent provides deep link: `https://workday.contoso.com/hr-service-center/complex-changes`

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
- Agent provides deep link: `https://workday.contoso.com/erlr/intake`
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
- Agent provides deep link: `https://workday.contoso.com/goos/request`
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

## Function Tool Behavior

The agent uses two function tools. During the demo, you'll see these being invoked:

### `get_change_type_guidance`
- **Input**: `change_type` (enum)
- **Output**: tier, documentation requirements, timeline, deep link, steps
- **Triggers on**: Any clear personal data change request

### `screen_grievance`
- **Input**: `concern_summary`, `involves_misconduct` (bool), `concern_category` (enum)
- **Output**: recommended path (ERLR/GOOS), reason, deep link, process, protections/key points
- **Triggers on**: Any workplace concern or grievance-related question

---

## Key Deep Links Reference

| Destination | URL |
|-------------|-----|
| ESS Portal | https://workday.contoso.com/ess/personal-data |
| Emergency Contacts | https://workday.contoso.com/ess/emergency-contacts |
| Preferred Name | https://workday.contoso.com/ess/preferred-name |
| Home Address | https://workday.contoso.com/ess/home-address |
| Complex Changes | https://workday.contoso.com/hr-service-center/complex-changes |
| Legal Name | https://workday.contoso.com/hr-service-center/legal-name |
| Passport/Visa | https://workday.contoso.com/hr-service-center/passport-visa |
| Payment Election | https://workday.contoso.com/hr-service-center/payment-election |
| ERLR Intake | https://workday.contoso.com/erlr/intake |
| GOOS Request | https://workday.contoso.com/goos/request |

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

## Workday Simulator

A local HTML simulator is available for demonstrating the deep link destinations:

```
C:\HRAgentService\workday-simulator\index.html
```

Open in a browser to show:
- **ESS page**: Emergency contact, address, preferred name, personal info forms
- **HR Service Center page**: Complex change type selector with upload
- **ERLR Intake page**: Full grievance filing form with incident details

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
│  │     │ Tools (x2)  │                                  │  │
│  │     └─────┬───────┘                                  │  │
│  └───────────┼──────────────────────────────────────────┘  │
│              │                                              │
└──────────────┼──────────────────────────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌──────────────┐   ┌──────────────┐
│get_change_   │   │screen_       │
│type_guidance │   │grievance     │
└──────┬───────┘   └──────┬───────┘
       │                   │
       ▼                   ▼
┌──────────────┐   ┌──────────────┐
│ESS / Complex │   │ERLR / GOOS   │
│Routing Logic │   │Routing Logic │
└──────────────┘   └──────────────┘

Supporting Infrastructure:
┌──────────────────────────────────────────┐
│ Azure AI Search (hr-concierge-search)    │
│ Index: hr-knowledge-base (13 documents)  │
│ - SharePoint HR policies (5 docs)        │
│ - ServiceNow KB articles (8 docs)        │
└──────────────────────────────────────────┘
┌──────────────────────────────────────────┐
│ External Systems                         │
│ - SharePoint: HR Docs library            │
│ - ServiceNow: KB articles (copilota2a)   │
│ - Workday Simulator: ESS/ERLR forms      │
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
