"""Create synthetic HR Knowledge Base articles in ServiceNow."""
import os
import requests
import json

INSTANCE = os.environ.get("SERVICENOW_INSTANCE", "https://copilota2a.service-now.com")
USER = os.environ.get("SERVICENOW_USER", "copilot.integration")
PASSWORD = os.environ["SERVICENOW_PASSWORD"]

# ServiceNow KB API endpoint
KB_API = f"{INSTANCE}/api/now/table/kb_knowledge"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# First, let's get or create a knowledge base
def get_or_create_kb():
    """Get existing HR knowledge base or create one."""
    # Check for existing KB
    resp = requests.get(
        f"{INSTANCE}/api/now/table/kb_knowledge_base",
        auth=(USER, PASSWORD),
        headers=HEADERS,
        params={"sysparm_query": "title=Contoso HR Knowledge Base", "sysparm_limit": 1}
    )
    resp.raise_for_status()
    results = resp.json().get("result", [])
    if results:
        print(f"Found existing KB: {results[0]['sys_id']}")
        return results[0]["sys_id"]
    
    # Create new KB
    resp = requests.post(
        f"{INSTANCE}/api/now/table/kb_knowledge_base",
        auth=(USER, PASSWORD),
        headers=HEADERS,
        json={
            "title": "Contoso HR Knowledge Base",
            "description": "Human Resources policies, procedures, and employee self-service guides for Contoso Corporation.",
            "active": "true"
        }
    )
    resp.raise_for_status()
    kb_id = resp.json()["result"]["sys_id"]
    print(f"Created KB: {kb_id}")
    return kb_id


# HR KB Articles - synthetic data for ServiceNow
ARTICLES = [
    {
        "short_description": "How to Change Your Emergency Contact in Workday",
        "text": """<h2>How to Change Your Emergency Contact in Workday</h2>
<p><strong>Category:</strong> Employee Self-Service | Personal Data Change</p>
<p><strong>Last Updated:</strong> May 2026</p>

<h3>Overview</h3>
<p>Employees can update their emergency contact information directly through Workday Employee Self-Service (ESS) without HR approval.</p>

<h3>Steps</h3>
<ol>
<li>Log in to <a href="https://contoso-workday.example.com/ess">Workday ESS Portal</a></li>
<li>Click on your profile icon in the top-right corner</li>
<li>Select <strong>Personal Information</strong> from the menu</li>
<li>Navigate to <strong>Emergency Contacts</strong></li>
<li>Click <strong>Edit</strong> to modify existing contacts or <strong>Add</strong> for new ones</li>
<li>Enter the contact's name, relationship, phone number, and email</li>
<li>Click <strong>Submit</strong></li>
</ol>

<h3>Important Notes</h3>
<ul>
<li>Changes take effect immediately</li>
<li>No manager or HR approval required</li>
<li>You can add up to 3 emergency contacts</li>
<li>At least one emergency contact is required per company policy</li>
</ul>

<h3>Troubleshooting</h3>
<p>If you cannot access the Emergency Contacts section, ensure your Workday session is active. If issues persist, contact HR Service Center at hr-help@contoso.com.</p>""",
        "workflow_state": "published",
        "category": "HR Self-Service"
    },
    {
        "short_description": "Legal Name Change Process and Requirements",
        "text": """<h2>Legal Name Change Process and Requirements</h2>
<p><strong>Category:</strong> Complex Personal Data Change | HR-Assisted</p>
<p><strong>Last Updated:</strong> May 2026</p>

<h3>Overview</h3>
<p>Legal name changes require HR assistance and supporting documentation. This applies to name changes due to marriage, divorce, court order, or gender transition.</p>

<h3>Required Documentation</h3>
<ul>
<li>Government-issued photo ID showing your new legal name (passport, driver's license)</li>
<li>Court order for legal name change, OR</li>
<li>Marriage certificate (for name change due to marriage), OR</li>
<li>Divorce decree (if reverting to maiden name)</li>
</ul>

<h3>Process</h3>
<ol>
<li>Gather required documentation (see above)</li>
<li>Submit request through <a href="https://contoso-workday.example.com/legal-name-change">Workday HR Service Center</a></li>
<li>Upload scanned copies of supporting documents</li>
<li>HR team reviews documentation (3-5 business days)</li>
<li>Once approved, name is updated across all systems (Workday, Active Directory, email, badge)</li>
<li>You will receive a confirmation email when complete</li>
</ol>

<h3>Important Notes</h3>
<ul>
<li>This is NOT a self-service change - HR review is required</li>
<li>Processing time: 3-5 business days after document submission</li>
<li>Your email address will be updated to reflect your new name (old alias maintained for 90 days)</li>
<li>Request a new badge from Security after name change is processed</li>
</ul>

<h3>Contact</h3>
<p>For questions about legal name changes, contact HR Service Center: hr-help@contoso.com</p>""",
        "workflow_state": "published",
        "category": "HR Complex Changes"
    },
    {
        "short_description": "How to Update Direct Deposit and Bank Details",
        "text": """<h2>How to Update Direct Deposit and Bank Details</h2>
<p><strong>Category:</strong> Complex Personal Data Change | Payment Election</p>
<p><strong>Last Updated:</strong> May 2026</p>

<h3>Overview</h3>
<p>Changes to your direct deposit, bank account, or payment method require verification by the Payroll team. Allow one full pay cycle for changes to take effect.</p>

<h3>Required Documentation</h3>
<ul>
<li>Voided check from the new bank account, OR</li>
<li>Official bank letter confirming account number and routing number</li>
<li>Bank statements are NOT accepted for security reasons</li>
</ul>

<h3>Process</h3>
<ol>
<li>Obtain a voided check or bank letter</li>
<li>Go to <a href="https://contoso-workday.example.com/payment-election">Workday Payment Election</a></li>
<li>Click <strong>Request Change</strong></li>
<li>Enter new bank name, routing number, and account number</li>
<li>Upload supporting documentation</li>
<li>Submit for Payroll review</li>
</ol>

<h3>Timeline</h3>
<ul>
<li>Submit by the 15th of the month for current pay cycle</li>
<li>Submissions after the 15th will apply to the following pay cycle</li>
<li>Payroll verifies within 2-3 business days</li>
<li>You'll receive confirmation email once processed</li>
</ul>

<h3>Security Notice</h3>
<p>For your protection, Contoso will never ask for bank details via email or phone. All payment changes must go through the official Workday portal.</p>""",
        "workflow_state": "published",
        "category": "HR Complex Changes"
    },
    {
        "short_description": "Filing a Workplace Grievance - ERLR Intake Process",
        "text": """<h2>Filing a Workplace Grievance - ERLR Intake Process</h2>
<p><strong>Category:</strong> Employee Relations & Labor Relations (ERLR)</p>
<p><strong>Last Updated:</strong> May 2026</p>

<h3>Overview</h3>
<p>If you are experiencing workplace harassment, discrimination, retaliation, or other serious workplace misconduct, you have the right to file a formal grievance through the Employee Relations & Labor Relations (ERLR) team.</p>

<h3>What Qualifies as a Formal Grievance?</h3>
<ul>
<li>Workplace harassment (sexual, racial, disability-based, or other protected characteristics)</li>
<li>Discrimination based on age, gender, race, religion, disability, sexual orientation, or national origin</li>
<li>Retaliation for reporting concerns or participating in an investigation</li>
<li>Bullying or intimidation creating a hostile work environment</li>
<li>Threats of violence or actual workplace violence</li>
<li>Ethical violations or fraud</li>
<li>Unsafe working conditions that management has failed to address</li>
</ul>

<h3>How to File</h3>
<ol>
<li>Access the <a href="https://contoso-workday.example.com/erlr-intake">ERLR Formal Intake Form</a></li>
<li>Provide a detailed description of the incident(s)</li>
<li>Include dates, times, and locations</li>
<li>List any witnesses</li>
<li>Describe your desired outcome</li>
<li>Submit the form</li>
</ol>

<h3>What Happens Next</h3>
<ul>
<li>An ERLR case manager is assigned within 48 hours</li>
<li>You will be contacted for an initial consultation</li>
<li>Investigation is conducted (typically 10-30 business days)</li>
<li>Resolution is communicated to all parties</li>
</ul>

<h3>Confidentiality & Non-Retaliation</h3>
<p>All reports are treated with strict confidentiality. Retaliation against anyone who files a grievance is strictly prohibited and will result in disciplinary action up to and including termination.</p>

<h3>Anonymous Reporting</h3>
<p>If you prefer to report anonymously, use the Contoso Ethics Hotline: 1-800-CONTOSO (available 24/7).</p>""",
        "workflow_state": "published",
        "category": "Employee Relations"
    },
    {
        "short_description": "Workplace Concerns That Are NOT Formal Grievances (GOOS)",
        "text": """<h2>Workplace Concerns That Are NOT Formal Grievances (GOOS)</h2>
<p><strong>Category:</strong> Employee Relations | Grievance Out-of-Scope</p>
<p><strong>Last Updated:</strong> May 2026</p>

<h3>Overview</h3>
<p>Not every workplace concern constitutes a formal grievance. Grievance Out-of-Scope (GOOS) issues are workplace annoyances or interpersonal conflicts that should be resolved through normal channels rather than the formal ERLR process.</p>

<h3>Examples of GOOS Issues</h3>
<ul>
<li>A coworker moved your chair, desk items, or personal belongings</li>
<li>Disagreements about meeting room bookings</li>
<li>Office temperature preferences</li>
<li>Colleague being too loud on phone calls</li>
<li>Disagreements about project approach or work priorities</li>
<li>Parking spot disputes</li>
<li>Kitchen or break room cleanliness</li>
<li>One-time rude comment that was NOT discriminatory</li>
<li>Schedule preference conflicts (not related to ADA accommodation)</li>
</ul>

<h3>How to Resolve GOOS Issues</h3>
<ol>
<li><strong>Direct Conversation:</strong> Talk to the other person respectfully about the issue</li>
<li><strong>Involve Your Manager:</strong> Ask your manager to facilitate a discussion</li>
<li><strong>Team Norms:</strong> Propose establishing team agreements about the issue</li>
<li><strong>Facilities Ticket:</strong> For environmental issues (temperature, noise), submit a facilities request</li>
<li><strong>Skip-Level:</strong> If the issue involves your manager, speak with their manager</li>
</ol>

<h3>When Does a GOOS Become a Grievance?</h3>
<p>A GOOS issue may escalate to a formal grievance if:</p>
<ul>
<li>The behavior becomes a pattern and creates a hostile environment</li>
<li>It involves discrimination based on a protected characteristic</li>
<li>The employee feels unsafe or threatened</li>
<li>Management has repeatedly failed to address the issue</li>
</ul>

<p>If you're unsure whether your concern is a grievance or GOOS, speak with HR Concierge for guidance.</p>""",
        "workflow_state": "published",
        "category": "Employee Relations"
    },
    {
        "short_description": "Preferred Name Change - Self-Service Guide",
        "text": """<h2>Preferred Name Change - Self-Service Guide</h2>
<p><strong>Category:</strong> Employee Self-Service | Personal Data Change</p>
<p><strong>Last Updated:</strong> May 2026</p>

<h3>Overview</h3>
<p>You can change your preferred (display) name in Workday without affecting your legal name records. Your preferred name will appear in Microsoft Teams, Outlook, the internal directory, and your door nameplate.</p>

<h3>Steps</h3>
<ol>
<li>Log in to <a href="https://contoso-workday.example.com/ess">Workday ESS Portal</a></li>
<li>Go to <strong>Personal Information</strong> > <strong>Preferred Name</strong></li>
<li>Click <strong>Edit</strong></li>
<li>Enter your preferred first name, middle name (optional), and last name</li>
<li>Click <strong>Submit</strong></li>
</ol>

<h3>Important Notes</h3>
<ul>
<li>No approval required - changes take effect within 24 hours</li>
<li>This does NOT change your legal name in payroll, tax, or benefits systems</li>
<li>Your email address will NOT change (use Legal Name Change process for email updates)</li>
<li>If you need both legal and preferred name changes, submit the legal name change FIRST</li>
<li>Preferred names must be appropriate for a professional workplace</li>
</ul>

<h3>Common Scenarios</h3>
<ul>
<li>"I go by a nickname" → Use preferred name change</li>
<li>"I got married and want my new last name" → Use preferred name change for display; legal name change for official records</li>
<li>"I'm transitioning and want my chosen name" → Use preferred name change (can do legal name change later)</li>
</ul>""",
        "workflow_state": "published",
        "category": "HR Self-Service"
    },
    {
        "short_description": "Passport and Visa Update Process",
        "text": """<h2>Passport and Visa Update Process</h2>
<p><strong>Category:</strong> Complex Personal Data Change | Immigration</p>
<p><strong>Last Updated:</strong> May 2026</p>

<h3>Overview</h3>
<p>When your passport or visa information changes, you must update your records with HR, especially if the change affects your work authorization. This is an HR-assisted process.</p>

<h3>When to Update</h3>
<ul>
<li>Passport renewal or replacement</li>
<li>New visa issuance or visa renewal</li>
<li>Change in immigration status</li>
<li>Work permit expiration approaching (notify HR 90 days before expiry)</li>
</ul>

<h3>Required Documentation</h3>
<ul>
<li>Copy of new passport (photo page)</li>
<li>Copy of new visa stamp or approval notice</li>
<li>I-9 re-verification form (if applicable for US employees)</li>
<li>Updated work permit or EAD card (if applicable)</li>
</ul>

<h3>Process</h3>
<ol>
<li>Access <a href="https://contoso-workday.example.com/passport-visa-update">Workday Passport/Visa Update Portal</a></li>
<li>Select the type of update (passport renewal, new visa, status change)</li>
<li>Upload required documents</li>
<li>Submit for Immigration team review</li>
</ol>

<h3>Timeline</h3>
<ul>
<li>Immigration team reviews within 5-7 business days</li>
<li>You may be asked to present original documents in person</li>
<li>I-9 re-verification must be completed before your current authorization expires</li>
</ul>

<h3>Contact</h3>
<p>Immigration Team: immigration@contoso.com | HR Service Center: hr-help@contoso.com</p>""",
        "workflow_state": "published",
        "category": "HR Complex Changes"
    },
    {
        "short_description": "Home Address and Contact Information Update",
        "text": """<h2>Home Address and Contact Information Update</h2>
<p><strong>Category:</strong> Employee Self-Service | Personal Data Change</p>
<p><strong>Last Updated:</strong> May 2026</p>

<h3>Overview</h3>
<p>Employees can update their home address, personal phone number, and personal email address directly through Workday ESS. No HR approval is required.</p>

<h3>Steps</h3>
<ol>
<li>Log in to <a href="https://contoso-workday.example.com/ess">Workday ESS Portal</a></li>
<li>Navigate to <strong>Personal Information</strong> > <strong>Contact Information</strong></li>
<li>Click <strong>Edit</strong> next to your home address or phone/email</li>
<li>Enter your updated information</li>
<li>Click <strong>Submit</strong></li>
</ol>

<h3>Important Notes</h3>
<ul>
<li>Address changes take effect immediately in HR systems</li>
<li>If you move to a different state/country, this may affect your tax withholdings - payroll will reach out if adjustments are needed</li>
<li>Update your emergency contacts separately if they've also moved</li>
<li>Benefits coverage may be affected by state changes - contact Benefits team</li>
</ul>

<h3>Impact of Address Change</h3>
<table>
<tr><th>System</th><th>Updated Automatically?</th></tr>
<tr><td>Workday</td><td>Yes - immediate</td></tr>
<tr><td>Payroll/Tax</td><td>Yes - next cycle</td></tr>
<tr><td>Benefits</td><td>May require separate update</td></tr>
<tr><td>Parking/Transit</td><td>No - update separately</td></tr>
</table>""",
        "workflow_state": "published",
        "category": "HR Self-Service"
    }
]


def create_articles(kb_id):
    """Create all KB articles in ServiceNow."""
    created = 0
    for article in ARTICLES:
        payload = {
            "short_description": article["short_description"],
            "text": article["text"],
            "workflow_state": article["workflow_state"],
            "kb_knowledge_base": kb_id,
            "article_type": "text",
            "active": "true"
        }
        
        resp = requests.post(
            KB_API,
            auth=(USER, PASSWORD),
            headers=HEADERS,
            json=payload
        )
        
        if resp.status_code in (200, 201):
            result = resp.json().get("result", {})
            print(f"  Created: {article['short_description']} (sys_id: {result.get('sys_id', 'N/A')})")
            created += 1
        else:
            print(f"  FAILED: {article['short_description']} - {resp.status_code}: {resp.text[:200]}")
    
    return created


if __name__ == "__main__":
    print("=" * 60)
    print("Creating ServiceNow HR Knowledge Base Articles")
    print("=" * 60)
    print(f"Instance: {INSTANCE}")
    print()

    # Get or create the knowledge base
    print("Step 1: Getting/Creating Knowledge Base...")
    kb_id = get_or_create_kb()
    print()

    # Create articles
    print(f"Step 2: Creating {len(ARTICLES)} KB articles...")
    count = create_articles(kb_id)
    print()
    print(f"Done! Created {count}/{len(ARTICLES)} articles successfully.")
    print(f"View in ServiceNow: {INSTANCE}/kb_knowledge_list.do")
