"""Create Azure AI Search index and upload HR knowledge base content."""
import os
import requests
import json

SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT", "https://hr-concierge-search.search.windows.net")
ADMIN_KEY = os.environ["AZURE_SEARCH_ADMIN_KEY"]
INDEX_NAME = "hr-knowledge-base"

headers = {
    "Content-Type": "application/json",
    "api-key": ADMIN_KEY
}

# Step 1: Create the index schema
index_schema = {
    "name": INDEX_NAME,
    "fields": [
        {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
        {"name": "title", "type": "Edm.String", "searchable": True, "filterable": True},
        {"name": "content", "type": "Edm.String", "searchable": True},
        {"name": "category", "type": "Edm.String", "filterable": True, "facetable": True},
        {"name": "source", "type": "Edm.String", "filterable": True},
        {"name": "url", "type": "Edm.String"},
        {"name": "keywords", "type": "Collection(Edm.String)", "searchable": True, "filterable": True}
    ],
    "semantic": {
        "configurations": [
            {
                "name": "hr-semantic-config",
                "prioritizedFields": {
                    "titleField": {"fieldName": "title"},
                    "prioritizedContentFields": [{"fieldName": "content"}],
                    "prioritizedKeywordsFields": [{"fieldName": "keywords"}]
                }
            }
        ],
        "defaultConfiguration": "hr-semantic-config"
    }
}

print("Creating search index...")
resp = requests.put(
    f"{SEARCH_ENDPOINT}/indexes/{INDEX_NAME}?api-version=2024-07-01",
    headers=headers,
    json=index_schema
)
print(f"  Status: {resp.status_code}")
if resp.status_code not in (200, 201):
    print(f"  Error: {resp.text}")
    exit(1)
print("  Index created successfully!")

# Step 2: Upload HR documents
documents = [
    {
        "id": "ess-guide-001",
        "title": "Employee Self-Service (ESS) Guide - Personal Data Changes",
        "content": """Employee Self-Service (ESS) Guide for Personal Data Changes at Contoso.

ESS Changes (No Approval Required - Immediate Effect):
- Emergency Contact: Update name, relationship, phone, email of emergency contacts
- Home Contact Information: Update street address, city, state, zip, country, personal phone, personal email
- Personal Information: Update marital status, date of marriage, pronouns
- Preferred Name: Update preferred first name and preferred last name (display name)

How to make ESS changes:
1. Log into Workday ESS Portal
2. Navigate to Personal Information section
3. Select the type of change you want to make
4. Enter new information
5. Submit - changes take effect immediately

Deep Link: https://workday.contoso.com/ess/personal-data

Important: ESS changes do NOT require manager approval or HR review. They are processed immediately upon submission.""",
        "category": "personal-data-changes",
        "source": "SharePoint",
        "url": "https://m365cpi47937014.sharepoint.com/sites/JohnsonandJohnsonHR/HR%20Docs/ESS_Personal_Data_Changes_Guide.docx",
        "keywords": ["ESS", "self-service", "emergency contact", "address", "preferred name", "personal information", "marital status"]
    },
    {
        "id": "complex-changes-001",
        "title": "Complex Personal Data Changes - HR Service Center Policy",
        "content": """Complex Personal Data Changes Policy - Requires Documentation & HR Review

Complex changes require supporting documentation and are reviewed by the HR Service Center within 3-5 business days.

Types of Complex Changes:
1. Legal Name Change - Requires court order, marriage certificate, or divorce decree
2. Passport & Visa Update - Requires copy of new passport/visa document
3. Government ID (SSN/Tax ID) - Requires new SSN card or tax document
4. Licenses & Certifications - Requires copy of new certificate/license
5. Payment Election (Bank Details) - Requires voided check or bank verification letter
6. Photo Change - New professional photo meeting company guidelines

Process:
1. Log into Workday HR Service Center portal
2. Select the type of complex change
3. Provide reason for change
4. Upload supporting documentation (PDF, JPG, PNG - max 10MB)
5. Add any additional notes for HR reviewer
6. Submit for review

Deep Link: https://workday.contoso.com/hr-service-center/complex-changes

Timeline: HR reviews within 3-5 business days. You will receive email confirmation when processed.
Escalation: If not processed within 5 days, contact HR Service Center at hr-service@contoso.com.""",
        "category": "personal-data-changes",
        "source": "SharePoint",
        "url": "https://m365cpi47937014.sharepoint.com/sites/JohnsonandJohnsonHR/HR%20Docs/Complex_Personal_Data_Changes_Policy.docx",
        "keywords": ["complex changes", "legal name", "passport", "bank details", "photo", "documentation", "HR review"]
    },
    {
        "id": "grievance-erlr-001",
        "title": "Formal Grievance & ERLR Policy",
        "content": """Formal Grievance Filing & Employee Relations/Labor Relations (ERLR) Policy

When to File a Formal Grievance (ERLR):
A formal grievance should be filed when the concern involves:
- Workplace harassment (sexual, verbal, physical)
- Discrimination (race, gender, age, disability, religion, national origin, sexual orientation)
- Retaliation against whistleblowers or reporters
- Bullying or hostile work environment
- Threats or violence in the workplace
- Ethical violations or fraud
- Unsafe working conditions
- Accommodation violations (ADA, religious)
- Other serious misconduct

ERLR Process:
1. Initial Screening: HR Concierge determines if the concern meets ERLR criteria
2. Intake Form: Employee completes confidential ERLR intake form
3. Case Assignment: ERLR case manager assigned within 48 hours
4. Investigation: Formal investigation conducted (typically 10-30 days)
5. Resolution: Findings communicated, corrective action taken if warranted
6. Appeal: Employee may appeal within 10 business days

Deep Link: https://workday.contoso.com/erlr/intake

Key Protections:
- All reports are CONFIDENTIAL
- Retaliation is PROHIBITED and subject to disciplinary action up to termination
- Anonymous reporting available through Ethics Hotline: 1-800-555-ETHICS

Contact: erlr@contoso.com | Ext. 5555""",
        "category": "grievance",
        "source": "SharePoint",
        "url": "https://m365cpi47937014.sharepoint.com/sites/JohnsonandJohnsonHR/HR%20Docs/Grievance_ERLR_Policy.docx",
        "keywords": ["grievance", "ERLR", "harassment", "discrimination", "formal complaint", "investigation", "confidential"]
    },
    {
        "id": "goos-001",
        "title": "Good Office Services (GOOS) - Informal Resolution Guide",
        "content": """Good Office Services (GOOS) - Informal Workplace Concern Resolution

What is GOOS?
Good Office Services provides informal, confidential support for everyday workplace concerns that don't rise to the level of formal ERLR investigation.

When to Use GOOS (NOT formal grievance):
- Interpersonal conflicts with coworkers
- Communication style differences
- Desk/workspace disputes
- Noise or environmental concerns
- Scheduling conflicts
- Team dynamics issues
- Minor disagreements with manager decisions
- Work-life balance discussions
- Feeling excluded from team activities
- Unclear expectations or role ambiguity

GOOS Process:
1. Contact GOOS coordinator (self-referral or HR referral)
2. Confidential intake conversation (30 minutes)
3. Options presented: mediation, coaching, facilitated conversation, referral
4. Resolution facilitated (typically 1-2 weeks)
5. Follow-up at 30 days

Important Distinctions:
- GOOS is VOLUNTARY - both parties must agree to participate
- GOOS is NOT a substitute for formal grievance when misconduct is involved
- No formal investigation or disciplinary action results from GOOS
- If misconduct is discovered during GOOS, it will be referred to ERLR

Deep Link: https://workday.contoso.com/goos/request

Contact: goos@contoso.com | Ext. 4444""",
        "category": "grievance",
        "source": "SharePoint",
        "url": "https://m365cpi47937014.sharepoint.com/sites/JohnsonandJohnsonHR/HR%20Docs/GOOS_Resolution_Guide.docx",
        "keywords": ["GOOS", "good office services", "informal", "mediation", "workplace conflict", "interpersonal"]
    },
    {
        "id": "hr-service-catalog-001",
        "title": "HR Service Catalog - Complete Reference",
        "content": """HR Service Catalog - Contoso Employee Services Reference

Tier 1 - Self-Service (ESS in Workday):
- Emergency contact updates
- Home address/contact changes
- Preferred name changes
- Marital status updates
- Pronoun preferences
Deep Link: https://workday.contoso.com/ess/personal-data

Tier 2 - HR Service Center (Documentation Required):
- Legal name changes
- Passport/visa updates
- Government ID changes
- Bank/payment election changes
- License/certification updates
- Photo changes
Deep Link: https://workday.contoso.com/hr-service-center/complex-changes

Tier 3 - Specialist Services:
- ERLR formal grievances: https://workday.contoso.com/erlr/intake
- GOOS informal resolution: https://workday.contoso.com/goos/request
- Benefits enrollment: https://workday.contoso.com/benefits
- Leave management: https://workday.contoso.com/leave
- Compensation inquiries: hr-comp@contoso.com

ServiceNow Knowledge Base:
- KB articles available at: https://copilota2a.service-now.com
- Search for step-by-step guides for each process

SLA Commitments:
- ESS changes: Immediate
- Complex changes: 3-5 business days
- ERLR case assignment: 48 hours
- GOOS intake: 2 business days""",
        "category": "service-catalog",
        "source": "SharePoint",
        "url": "https://m365cpi47937014.sharepoint.com/sites/JohnsonandJohnsonHR/HR%20Docs/HR_Service_Catalog.docx",
        "keywords": ["service catalog", "HR services", "tier 1", "tier 2", "tier 3", "SLA"]
    },
    {
        "id": "sn-emergency-contact-001",
        "title": "How to Update Emergency Contacts in Workday",
        "content": """Step-by-step guide to update your emergency contact information in Workday ESS.

Steps:
1. Log into Workday at https://workday.contoso.com
2. Click on your profile icon (top right)
3. Select 'Personal Information' from the menu
4. Click 'Emergency Contacts' section
5. Click 'Edit' or 'Add' button
6. Enter contact details: Full Name, Relationship, Phone Number, Email
7. Set priority order if multiple contacts
8. Click 'Submit'

Your changes take effect immediately. No approval required.

Tips:
- You can have up to 3 emergency contacts
- At least one contact is required by company policy
- International phone numbers are supported
- You'll receive a confirmation email after submission

Deep Link: https://workday.contoso.com/ess/emergency-contacts""",
        "category": "personal-data-changes",
        "source": "ServiceNow",
        "url": "https://copilota2a.service-now.com/kb_view.do?sys_kb_id=emergency-contacts",
        "keywords": ["emergency contact", "ESS", "step-by-step", "Workday"]
    },
    {
        "id": "sn-legal-name-001",
        "title": "Legal Name Change Process - Step by Step",
        "content": """How to request a legal name change through the HR Service Center.

Prerequisites:
- Court-issued name change order, OR
- Marriage certificate, OR
- Divorce decree showing new legal name

Steps:
1. Log into Workday at https://workday.contoso.com
2. Navigate to HR Service Center > Complex Changes
3. Select 'Legal Name Change' from the dropdown
4. Enter your new legal first name and last name
5. Provide reason (marriage, divorce, court order, other)
6. Upload supporting document (PDF or clear photo, max 10MB)
7. Add any notes for the reviewer
8. Submit request

After Submission:
- You'll receive a case number via email immediately
- HR reviews within 3-5 business days
- If additional documentation needed, HR will contact you
- Once approved, name updates in all systems within 24 hours
- New ID badge can be requested after approval

Deep Link: https://workday.contoso.com/hr-service-center/legal-name

Note: Your preferred name can be changed immediately via ESS without documentation.""",
        "category": "personal-data-changes",
        "source": "ServiceNow",
        "url": "https://copilota2a.service-now.com/kb_view.do?sys_kb_id=legal-name",
        "keywords": ["legal name", "name change", "marriage", "divorce", "court order", "documentation"]
    },
    {
        "id": "sn-direct-deposit-001",
        "title": "How to Change Direct Deposit / Bank Details",
        "content": """Guide to updating your payment election (direct deposit / bank details).

Prerequisites:
- Voided check from new bank account, OR
- Bank verification letter (on bank letterhead, within 30 days)

Steps:
1. Log into Workday at https://workday.contoso.com
2. Navigate to HR Service Center > Complex Changes
3. Select 'Payment Election (Bank Details)'
4. Enter new bank routing number and account number
5. Select account type (checking/savings)
6. Upload voided check or bank letter
7. Submit for review

Processing:
- HR validates documentation within 3-5 business days
- If approved before payroll cutoff (15th/last day), effective next pay period
- If after cutoff, effective following pay period
- You'll receive confirmation email with effective date

Security:
- Old account remains active until new election is confirmed
- Split deposits can be configured (up to 3 accounts)
- International bank accounts require additional SWIFT/IBAN documentation

Deep Link: https://workday.contoso.com/hr-service-center/payment-election""",
        "category": "personal-data-changes",
        "source": "ServiceNow",
        "url": "https://copilota2a.service-now.com/kb_view.do?sys_kb_id=direct-deposit",
        "keywords": ["direct deposit", "bank", "payment election", "routing number", "voided check"]
    },
    {
        "id": "sn-grievance-filing-001",
        "title": "How to File a Formal Workplace Grievance (ERLR)",
        "content": """Step-by-step guide to filing a formal grievance through ERLR.

Before Filing - Is This ERLR?
Your concern qualifies for ERLR if it involves:
✓ Harassment (sexual, verbal, physical)
✓ Discrimination (protected characteristics)
✓ Retaliation
✓ Bullying/hostile work environment
✓ Threats or violence
✓ Ethical violations/fraud
✓ Safety violations
✓ Accommodation violations

Your concern is better suited for GOOS if it involves:
✗ Interpersonal conflicts
✗ Communication differences
✗ Scheduling disputes
✗ Team dynamics
✗ Minor disagreements

Filing Steps:
1. Log into Workday at https://workday.contoso.com
2. Navigate to ERLR Intake
3. Select type of concern from dropdown
4. Provide detailed description of incident(s)
5. Enter date(s), location, persons involved
6. List any witnesses
7. Indicate previous reporting attempts
8. State desired outcome
9. Upload any evidence (emails, screenshots, etc.)
10. Select preferred contact method and availability
11. Submit

After Filing:
- Case reference number issued immediately (format: ERLR-YYYY-XXXX)
- ERLR case manager assigned within 48 hours
- Initial contact via your preferred method
- Investigation typically 10-30 calendar days
- Confidentiality maintained throughout

Deep Link: https://workday.contoso.com/erlr/intake

Emergency: If you feel in immediate danger, contact Security at Ext. 9999 or call 911.""",
        "category": "grievance",
        "source": "ServiceNow",
        "url": "https://copilota2a.service-now.com/kb_view.do?sys_kb_id=grievance-filing",
        "keywords": ["grievance", "ERLR", "formal complaint", "filing", "harassment", "discrimination"]
    },
    {
        "id": "sn-goos-request-001",
        "title": "How to Request Good Office Services (GOOS)",
        "content": """Guide to requesting informal workplace resolution through GOOS.

What GOOS Helps With:
- Interpersonal conflicts between colleagues
- Communication breakdowns
- Team dynamics issues
- Minor workplace disputes
- Feeling excluded or marginalized (not discrimination)
- Unclear expectations
- Work-life balance concerns
- Manager relationship coaching

Steps to Request:
1. Log into Workday at https://workday.contoso.com
2. Navigate to GOOS Request
3. Briefly describe your concern
4. Indicate if other party is aware of the request
5. Select preferred resolution approach (mediation, coaching, facilitation)
6. Submit request

After Submission:
- GOOS coordinator contacts you within 2 business days
- 30-minute confidential intake conversation
- Options discussed and agreed upon
- Resolution typically facilitated within 1-2 weeks
- Follow-up at 30 days

Key Points:
- Participation is VOLUNTARY for all parties
- Content is CONFIDENTIAL
- No disciplinary action results from GOOS
- You can withdraw at any time
- If misconduct is discovered, automatic referral to ERLR

Deep Link: https://workday.contoso.com/goos/request""",
        "category": "grievance",
        "source": "ServiceNow",
        "url": "https://copilota2a.service-now.com/kb_view.do?sys_kb_id=goos-request",
        "keywords": ["GOOS", "good office services", "informal resolution", "mediation", "workplace conflict"]
    },
    {
        "id": "sn-preferred-name-001",
        "title": "How to Update Your Preferred Name",
        "content": """Quick guide to changing your preferred/display name in Workday.

This is an ESS (self-service) change - no approval or documentation required!

Steps:
1. Log into Workday at https://workday.contoso.com
2. Click your profile icon > Personal Information
3. Click 'Preferred Name' section
4. Enter your preferred first name and/or last name
5. Click Submit

Your preferred name will update in:
- Email display name: within 24 hours
- Teams/Slack display: within 24 hours
- Company directory: within 24 hours
- Door nameplate: submit separate facilities request
- Business cards: submit reprint request

Note: This changes your DISPLAY name only. Your legal name remains unchanged in payroll, tax, and official documents. To change your legal name, use the Complex Changes process.

Deep Link: https://workday.contoso.com/ess/preferred-name""",
        "category": "personal-data-changes",
        "source": "ServiceNow",
        "url": "https://copilota2a.service-now.com/kb_view.do?sys_kb_id=preferred-name",
        "keywords": ["preferred name", "display name", "ESS", "self-service"]
    },
    {
        "id": "sn-passport-visa-001",
        "title": "How to Update Passport or Visa Information",
        "content": """Guide to updating passport or visa details through HR Service Center.

When to Update:
- New passport issued (renewal or replacement)
- Visa status change (new visa, extension, change of status)
- Work authorization change
- Travel document updates

Prerequisites:
- Clear copy/scan of new passport photo page, OR
- Copy of new visa stamp/approval notice
- Must be legible and unexpired

Steps:
1. Log into Workday at https://workday.contoso.com
2. Navigate to HR Service Center > Complex Changes
3. Select 'Passport & Visa Update'
4. Enter document type, number, country of issue, expiration date
5. Upload clear copy of document
6. Submit for review

Processing:
- HR validates within 3-5 business days
- May require in-person verification of original document
- I-9 reverification may be triggered for visa changes
- You'll be contacted if additional action needed

Important:
- Keep your travel documents current - expired documents may affect business travel approval
- Notify HR immediately if work authorization is changing
- Do not travel internationally if passport expires within 6 months

Deep Link: https://workday.contoso.com/hr-service-center/passport-visa""",
        "category": "personal-data-changes",
        "source": "ServiceNow",
        "url": "https://copilota2a.service-now.com/kb_view.do?sys_kb_id=passport-visa",
        "keywords": ["passport", "visa", "travel document", "work authorization", "I-9"]
    },
    {
        "id": "sn-home-address-001",
        "title": "How to Change Your Home Address",
        "content": """Quick guide to updating your home address in Workday ESS.

This is an ESS (self-service) change - takes effect immediately!

Steps:
1. Log into Workday at https://workday.contoso.com
2. Click your profile icon > Personal Information
3. Click 'Home Contact Information' section
4. Click 'Edit' on your address
5. Enter new street address, city, state, zip, country
6. Update phone number if changed
7. Click Submit

Takes Effect:
- HR records: Immediately
- Payroll/tax withholding: Next pay period (may affect state tax)
- Benefits (if moving states): Contact benefits team
- Mail/correspondence: Within 1 week

Important Considerations:
- If moving to a different STATE: Tax withholding may change. Review your next paycheck.
- If moving to a different COUNTRY: Contact HR Global Mobility BEFORE moving.
- If you need a letter confirming employment at new address: Request from HR Service Center.
- P.O. Box: Can be used for mailing address but physical address also required.

Deep Link: https://workday.contoso.com/ess/home-address""",
        "category": "personal-data-changes",
        "source": "ServiceNow",
        "url": "https://copilota2a.service-now.com/kb_view.do?sys_kb_id=home-address",
        "keywords": ["home address", "address change", "ESS", "move", "relocation"]
    }
]

# Upload documents
print(f"\nUploading {len(documents)} documents to index...")
upload_body = {"value": [{"@search.action": "upload", **doc} for doc in documents]}

resp = requests.post(
    f"{SEARCH_ENDPOINT}/indexes/{INDEX_NAME}/docs/index?api-version=2024-07-01",
    headers=headers,
    json=upload_body
)
print(f"  Status: {resp.status_code}")
if resp.status_code in (200, 207):
    result = resp.json()
    success = sum(1 for v in result["value"] if v["status"])
    print(f"  Successfully uploaded: {success}/{len(documents)} documents")
else:
    print(f"  Error: {resp.text}")

print("\nDone! Index ready for agent consumption.")
