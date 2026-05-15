"""Test the HR Concierge agent with sample conversations."""
import requests
import subprocess
import time
import json
import os

PROJECT_ENDPOINT = "https://hr-concierge-ai.services.ai.azure.com/api/projects/hr-concierge-project"
AGENT_ID = "asst_sqktCaGkeebbWfuGPtNgnQjo"
SEARCH_ENDPOINT = "https://hr-concierge-search.search.windows.net"
SEARCH_INDEX = "hr-knowledge-base"
SEARCH_KEY = os.environ.get("AZURE_SEARCH_ADMIN_KEY", "")

def get_token():
    result = subprocess.run(
        'az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv',
        capture_output=True, text=True, shell=True
    )
    return result.stdout.strip()

def test_agent(message, test_name):
    token = get_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"USER: {message}")
    print(f"{'='*60}")
    
    # Create a thread
    resp = requests.post(f"{PROJECT_ENDPOINT}/threads?api-version=2025-05-01", headers=headers, json={})
    if resp.status_code not in (200, 201):
        print(f"  ❌ Thread creation failed: {resp.status_code} - {resp.text}")
        return
    thread = resp.json()
    thread_id = thread["id"]
    
    # Add a message
    resp = requests.post(
        f"{PROJECT_ENDPOINT}/threads/{thread_id}/messages?api-version=2025-05-01",
        headers=headers,
        json={"role": "user", "content": message}
    )
    if resp.status_code not in (200, 201):
        print(f"  ❌ Message creation failed: {resp.status_code} - {resp.text}")
        return
    
    # Create a run
    resp = requests.post(
        f"{PROJECT_ENDPOINT}/threads/{thread_id}/runs?api-version=2025-05-01",
        headers=headers,
        json={"assistant_id": AGENT_ID}
    )
    if resp.status_code not in (200, 201):
        print(f"  ❌ Run creation failed: {resp.status_code} - {resp.text}")
        return
    run = resp.json()
    run_id = run["id"]
    
    # Poll for completion
    for _ in range(30):
        time.sleep(2)
        resp = requests.get(
            f"{PROJECT_ENDPOINT}/threads/{thread_id}/runs/{run_id}?api-version=2025-05-01",
            headers=headers
        )
        run_status = resp.json()
        status = run_status.get("status", "unknown")
        
        if status == "completed":
            break
        elif status == "requires_action":
            # Handle function tool calls
            tool_calls = run_status.get("required_action", {}).get("submit_tool_outputs", {}).get("tool_calls", [])
            tool_outputs = []
            for tc in tool_calls:
                func_name = tc["function"]["name"]
                func_args = json.loads(tc["function"]["arguments"])
                print(f"  🔧 Tool called: {func_name}({json.dumps(func_args, indent=2)})")
                
                # Simulate tool responses
                if func_name == "get_change_type_guidance":
                    output = get_change_guidance_response(func_args["change_type"])
                elif func_name == "screen_grievance":
                    output = get_grievance_response(func_args)
                elif func_name == "search_hr_knowledge_base":
                    output = search_knowledge_base(func_args.get("query", ""), func_args.get("top_results", 3))
                else:
                    output = json.dumps({"error": "Unknown function"})
                
                tool_outputs.append({"tool_call_id": tc["id"], "output": output})
            
            # Submit tool outputs
            resp = requests.post(
                f"{PROJECT_ENDPOINT}/threads/{thread_id}/runs/{run_id}/submit_tool_outputs?api-version=2025-05-01",
                headers=headers,
                json={"tool_outputs": tool_outputs}
            )
        elif status in ("failed", "cancelled", "expired"):
            print(f"  ❌ Run {status}: {run_status.get('last_error', {})}")
            return
    
    # Get messages
    resp = requests.get(
        f"{PROJECT_ENDPOINT}/threads/{thread_id}/messages?api-version=2025-05-01",
        headers=headers
    )
    messages = resp.json().get("data", [])
    
    # Get the assistant's response (most recent assistant message)
    for msg in messages:
        if msg["role"] == "assistant":
            for content in msg.get("content", []):
                if content.get("type") == "text":
                    print(f"\n  AGENT RESPONSE:")
                    print(f"  {content['text']['value'][:500]}")
            break
    
    print()

def search_knowledge_base(query, top_results=3):
    """Call Azure AI Search to query the HR knowledge base."""
    if not SEARCH_KEY:
        return json.dumps({"error": "AZURE_SEARCH_ADMIN_KEY not set"})
    headers = {"api-key": SEARCH_KEY, "Content-Type": "application/json"}
    body = {
        "search": query,
        "queryType": "semantic",
        "semanticConfiguration": "hr-semantic-config",
        "top": min(top_results, 5),
        "select": "title,content,source"
    }
    resp = requests.post(
        f"{SEARCH_ENDPOINT}/indexes/{SEARCH_INDEX}/docs/search?api-version=2024-07-01",
        headers=headers, json=body
    )
    if resp.status_code == 200:
        results = resp.json().get("value", [])
        docs = []
        for doc in results:
            snippet = doc.get("content", "")[:500]
            docs.append(f"## {doc.get('title', 'Untitled')}\n{snippet}\nSource: {doc.get('source', 'Unknown')}")
        return "\n---\n".join(docs) if docs else "No results found."
    return json.dumps({"error": f"Search failed: {resp.status_code}"})


def get_change_guidance_response(change_type):
    """Simulate the get_change_type_guidance function response."""
    ess_types = ["emergency_contact", "home_address", "preferred_name", "personal_info"]
    
    if change_type in ess_types:
        return json.dumps({
            "tier": "ESS (Self-Service)",
            "approval_required": False,
            "documentation_required": False,
            "timeline": "Immediate",
            "deep_link": "https://workday.contoso.com/ess/personal-data",
            "steps": [
                "Log into Workday ESS Portal",
                "Navigate to Personal Information",
                f"Select '{change_type.replace('_', ' ').title()}'",
                "Enter new information",
                "Submit - changes take effect immediately"
            ]
        })
    else:
        docs = {
            "legal_name": "Court order, marriage certificate, or divorce decree",
            "passport_visa": "Copy of new passport/visa document",
            "government_id": "New SSN card or tax document",
            "licenses": "Copy of new certificate/license",
            "bank_details": "Voided check or bank verification letter",
            "photo": "New professional photo meeting company guidelines"
        }
        return json.dumps({
            "tier": "HR Service Center (Complex)",
            "approval_required": True,
            "documentation_required": True,
            "required_documentation": docs.get(change_type, "Supporting documentation"),
            "timeline": "3-5 business days",
            "deep_link": "https://workday.contoso.com/hr-service-center/complex-changes",
            "steps": [
                "Log into Workday HR Service Center",
                f"Select '{change_type.replace('_', ' ').title()}'",
                "Provide reason for change",
                "Upload supporting documentation",
                "Submit for review"
            ]
        })

def get_grievance_response(args):
    """Simulate the screen_grievance function response."""
    erlr_categories = ["harassment", "discrimination", "retaliation", "bullying", 
                       "threats_violence", "ethical_violation", "safety", "accommodation"]
    
    if args.get("involves_misconduct") or args.get("concern_category") in erlr_categories:
        return json.dumps({
            "recommended_path": "ERLR (Formal Grievance)",
            "reason": "This concern involves potential serious misconduct that requires formal investigation.",
            "deep_link": "https://workday.contoso.com/erlr/intake",
            "process": "Intake form → Case manager (48hrs) → Investigation (10-30 days) → Resolution",
            "protections": ["Confidential", "Retaliation prohibited", "Anonymous option via Ethics Hotline"],
            "sla": "Case manager assigned within 48 hours"
        })
    else:
        return json.dumps({
            "recommended_path": "GOOS (Good Office Services)",
            "reason": "This concern is better suited for informal resolution through mediation or coaching.",
            "deep_link": "https://workday.contoso.com/goos/request",
            "process": "Self-referral → Intake conversation (2 days) → Options → Resolution (1-2 weeks)",
            "key_points": ["Voluntary for all parties", "Confidential", "No disciplinary action"],
            "sla": "GOOS coordinator contact within 2 business days"
        })


if __name__ == "__main__":
    print("🧪 HR Concierge Agent - Integration Test")
    print("=" * 60)
    
    # Test 1: ESS personal data change
    test_agent(
        "I just got married and need to update my last name. What do I need to do?",
        "Legal Name Change (Complex)"
    )
    
    # Test 2: Simple ESS change
    test_agent(
        "I need to add a new emergency contact. How do I do that?",
        "Emergency Contact Update (ESS)"
    )
    
    # Test 3: Grievance - ERLR
    test_agent(
        "My manager has been making inappropriate comments about my ethnicity. It's been happening for weeks and I want to file a complaint.",
        "Discrimination Grievance (ERLR)"
    )
    
    # Test 4: Grievance - GOOS
    test_agent(
        "My coworker plays music too loudly and won't use headphones despite me asking. It's affecting my work.",
        "Workspace Dispute (GOOS)"
    )
    
    # Test 5: Search-grounded query
    test_agent(
        "Can you search the knowledge base for information about the ERLR investigation timeline and appeal process?",
        "Knowledge Base Search (Foundry IQ)"
    )
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
