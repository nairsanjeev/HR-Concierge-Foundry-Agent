# HR Concierge — Azure AI Foundry Agent

An intelligent HR assistant built as a **native prompt agent** on Microsoft Azure AI Foundry. Handles employee personal data changes and workplace grievance screening with enterprise-grade security and responsible AI.

## What It Does

| Capability | Description |
|-----------|-------------|
| **Personal Data Changes** | Routes employees to the correct process — ESS self-service (immediate) or HR Service Center (documentation required, 3-5 day review) |
| **Grievance Screening** | Determines if a workplace concern should go through formal ERLR investigation or informal GOOS mediation |
| **Deep Linking** | Provides direct Workday portal links for each action |

## Architecture

- **Agent**: Native prompt agent (no containers/hosting required)
- **Model**: gpt-5.4-mini (DataZoneStandard)
- **Knowledge**: Azure AI Search with semantic ranking (13 HR documents)
- **Sources**: SharePoint Online + ServiceNow Knowledge Base
- **Auth**: Microsoft Entra ID (RBAC)
- **Tools**: 2 function tools (`get_change_type_guidance`, `screen_grievance`)

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed diagrams and platform value analysis.

## Project Structure

```
├── create_agent.py            # Creates the native prompt agent in Foundry
├── create_search_index.py     # Builds Azure AI Search index with HR content
├── create_servicenow_kb.py    # Generates ServiceNow KB articles
├── generate_hr_docs.py        # Generates SharePoint HR policy documents
├── test_agent.py              # Integration tests (4 scenarios)
├── workday-simulator/         # HTML simulator for Workday deep links
│   └── index.html
├── sharepoint-docs/           # Generated Word documents for SharePoint
├── ARCHITECTURE.md            # Architecture diagrams (Mermaid)
├── DEMO_GUIDE.md              # 40+ test prompts across 8 scenarios
├── .env.example               # Environment variable template
└── .gitignore
```

## Quick Start

### Prerequisites
- Azure subscription with AI Services resource
- Python 3.10+
- Azure CLI (`az login`)

### Setup

```bash
# Clone and set up
git clone https://github.com/YOUR_USERNAME/hr-concierge-foundry-agent.git
cd hr-concierge-foundry-agent
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install requests python-docx azure-ai-agents azure-identity

# Configure secrets
cp .env.example .env
# Edit .env with your actual keys
```

### Deploy the Agent

```bash
# 1. Create search index and upload HR knowledge
python create_search_index.py

# 2. Create the agent in Foundry
python create_agent.py

# 3. Test it
python test_agent.py
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `AZURE_SEARCH_ENDPOINT` | Azure AI Search endpoint URL |
| `AZURE_SEARCH_ADMIN_KEY` | Search service admin key |
| `SERVICENOW_INSTANCE` | ServiceNow instance URL |
| `SERVICENOW_USER` | ServiceNow integration user |
| `SERVICENOW_PASSWORD` | ServiceNow password |

The agent itself authenticates via `az account get-access-token` (Azure CLI credential).

## Testing

Run the integration test suite:

```bash
python test_agent.py
```

Tests 4 scenarios:
1. Legal name change → routed to Complex/HR Service Center
2. Emergency contact → routed to ESS/Self-service
3. Discrimination complaint → routed to ERLR formal grievance
4. Noise dispute → routed to GOOS informal resolution

See [DEMO_GUIDE.md](DEMO_GUIDE.md) for 40+ additional test prompts.

## Key Links

- **Foundry Portal**: https://ai.azure.com
- **Workday Simulator**: Open `workday-simulator/index.html` locally

## License

MIT
