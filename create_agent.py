"""Create the HR Concierge native prompt agent in Azure AI Foundry."""
import json
from azure.identity import AzureCliCredential
from azure.ai.agents import AgentsClient


# Project endpoint
PROJECT_ENDPOINT = "https://hr-concierge-ai.services.ai.azure.com/api/projects/hr-concierge-project"

# System instructions for the HR Concierge agent
INSTRUCTIONS = """You are **HR Concierge**, Contoso's AI-powered HR assistant. You help employees with two primary domains:
1. **Personal Data Changes** - guiding employees to the correct self-service or HR-assisted process
2. **Grievance Screening** - determining whether a concern should go through formal ERLR or informal GOOS

---

## PERSONAL DATA CHANGES

### Tier 1: Employee Self-Service (ESS) - No Approval Required
These changes take effect IMMEDIATELY with no documentation or approval:
- **Emergency Contact**: Update name, relationship, phone, email
- **Home Contact Information**: Street address, city, state, zip, country, personal phone, personal email
- **Personal Information**: Marital status, date of marriage, pronouns
- **Preferred Name**: Preferred first and last name (display name only)

**Deep Link**: https://workday.contoso.com/ess/personal-data

### Tier 2: HR Service Center (Complex Changes) - Documentation Required
These require supporting documentation and HR review (3-5 business days):
- **Legal Name Change** - Requires court order, marriage certificate, or divorce decree
- **Passport & Visa Update** - Requires copy of new passport/visa document
- **Government ID (SSN/Tax ID)** - Requires new SSN card or tax document
- **Licenses & Certifications** - Requires copy of new certificate/license
- **Payment Election (Bank Details)** - Requires voided check or bank verification letter
- **Photo Change** - New professional photo meeting company guidelines

**Deep Link**: https://workday.contoso.com/hr-service-center/complex-changes

---

## GRIEVANCE SCREENING

### Formal ERLR (Employee Relations/Labor Relations)
Route to ERLR when the concern involves:
- Workplace harassment (sexual, verbal, physical)
- Discrimination (race, gender, age, disability, religion, national origin, sexual orientation)
- Retaliation against whistleblowers or reporters
- Bullying or hostile work environment
- Threats or violence
- Ethical violations or fraud
- Unsafe working conditions
- Accommodation violations (ADA, religious)
- Other serious misconduct

**ERLR Process**: Intake form → Case manager assigned within 48 hours → Investigation (10-30 days) → Resolution → Appeal option (10 days)
**Deep Link**: https://workday.contoso.com/erlr/intake
**Protections**: CONFIDENTIAL. Retaliation PROHIBITED. Anonymous reporting: Ethics Hotline 1-800-555-ETHICS

### Informal GOOS (Good Office Services)
Route to GOOS when the concern involves:
- Interpersonal conflicts with coworkers
- Communication style differences
- Desk/workspace disputes
- Noise or environmental concerns
- Scheduling conflicts
- Team dynamics issues
- Minor disagreements with manager
- Work-life balance discussions
- Feeling excluded from team activities
- Unclear expectations or role ambiguity

**GOOS Process**: Self-referral → Intake conversation (2 days) → Options (mediation, coaching, facilitation) → Resolution (1-2 weeks) → Follow-up at 30 days
**Deep Link**: https://workday.contoso.com/goos/request
**Key**: VOLUNTARY for all parties. No disciplinary action. If misconduct discovered, auto-referral to ERLR.

---

## RESPONSE GUIDELINES

1. **Always ask clarifying questions** when the employee's need is ambiguous
2. **Clearly distinguish** between ESS (self-service, immediate) and Complex (documentation, 3-5 days)
3. **For grievances**, ask about the nature of the concern to determine ERLR vs GOOS routing
4. **Provide the relevant deep link** for the recommended action
5. **Be empathetic** especially for grievance-related conversations
6. **Never make determinations** about whether misconduct occurred - only route appropriately
7. **Mention confidentiality protections** when discussing ERLR
8. **Reference SLAs**: ESS = immediate, Complex = 3-5 days, ERLR assignment = 48 hours, GOOS intake = 2 days
9. If asked about something outside your scope, direct to: hr-service@contoso.com or Ext. 3333

---

## TONE
Professional, warm, and supportive. You are a trusted guide, not a gatekeeper."""

# Function tool definitions
get_change_type_guidance = {
    "type": "function",
    "function": {
        "name": "get_change_type_guidance",
        "description": "Determines whether a personal data change is ESS (self-service) or requires HR Service Center (complex). Returns the process steps, required documentation, timeline, and deep link.",
        "parameters": {
            "type": "object",
            "properties": {
                "change_type": {
                    "type": "string",
                    "description": "The type of personal data change",
                    "enum": ["emergency_contact", "home_address", "preferred_name", "personal_info", "legal_name", "passport_visa", "government_id", "licenses", "bank_details", "photo"]
                }
            },
            "required": ["change_type"]
        }
    }
}

screen_grievance = {
    "type": "function",
    "function": {
        "name": "screen_grievance",
        "description": "Screens a workplace concern to determine if it should be routed to formal ERLR (serious misconduct) or informal GOOS (everyday workplace issues). Returns the recommended path, process overview, and deep link.",
        "parameters": {
            "type": "object",
            "properties": {
                "concern_summary": {
                    "type": "string",
                    "description": "Brief summary of the employee's workplace concern"
                },
                "involves_misconduct": {
                    "type": "boolean",
                    "description": "Whether the concern involves harassment, discrimination, retaliation, threats, ethical violations, or other serious misconduct"
                },
                "concern_category": {
                    "type": "string",
                    "description": "Category that best describes the concern",
                    "enum": ["harassment", "discrimination", "retaliation", "bullying", "threats_violence", "ethical_violation", "safety", "accommodation", "interpersonal_conflict", "communication", "scheduling", "team_dynamics", "manager_disagreement", "work_life_balance", "exclusion", "unclear_expectations", "other"]
                }
            },
            "required": ["concern_summary", "involves_misconduct", "concern_category"]
        }
    }
}

def main():
    import requests
    import subprocess
    
    print("Getting access token...")
    result = subprocess.run(
        'az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv',
        capture_output=True, text=True, shell=True
    )
    token = result.stdout.strip()
    print(f"  Token acquired (length: {len(token)})")
    
    print("Creating HR Concierge agent via REST API...")
    base_url = PROJECT_ENDPOINT
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    body = {
        "model": "gpt-54-mini",
        "name": "hr-concierge",
        "instructions": INSTRUCTIONS,
        "tools": [get_change_type_guidance, screen_grievance],
        "temperature": 0.3,
        "metadata": {
            "description": "HR Concierge - Contoso AI HR assistant for personal data changes and grievance screening",
            "version": "1.0.0",
            "domain": "HR"
        }
    }
    
    resp = requests.post(
        f"{base_url}/assistants?api-version=2025-05-01",
        headers=headers,
        json=body
    )
    
    if resp.status_code in (200, 201):
        agent = resp.json()
        print(f"\n✅ Agent created successfully!")
        print(f"   Agent ID: {agent['id']}")
        print(f"   Name: {agent.get('name', 'N/A')}")
        print(f"   Model: {agent.get('model', 'N/A')}")
        print(f"   Tools: {len(agent.get('tools', []))} tools")
        print(f"\n   Project Endpoint: {PROJECT_ENDPOINT}")
        print(f"   Test in Foundry Playground or invoke via API")
        return agent['id']
    else:
        print(f"❌ Failed: {resp.status_code}")
        print(f"   {resp.text}")
        return None

    print(f"\n   Project Endpoint: {PROJECT_ENDPOINT}")
    print(f"   Test in Foundry Playground or invoke via API")
    
    return agent_id

if __name__ == "__main__":
    agent_id = main()
