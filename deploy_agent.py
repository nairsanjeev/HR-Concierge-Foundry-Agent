import json, subprocess, requests

token = subprocess.run(
    'az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv',
    capture_output=True, text=True, shell=True
).stdout.strip()

base_url = 'https://hr-concierge-ai.services.ai.azure.com/api/projects/hr-concierge-project'
headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

with open('agent_instructions.txt', 'r') as f:
    instructions = f.read()

with open('agent_body.json', 'r') as f:
    body = json.load(f)

body['instructions'] = instructions

resp = requests.post(
    f'{base_url}/assistants?api-version=2025-05-01',
    headers=headers,
    json=body
)

if resp.status_code == 200:
    agent = resp.json()
    print(f"SUCCESS - New Agent ID: {agent['id']}")
    print(f"Name: {agent['name']}")
    print(f"Model: {agent['model']}")
    print(f"Tools count: {len(agent['tools'])}")
    tool_types = [t['type'] for t in agent['tools']]
    print(f"Tool types: {tool_types}")
    tr = agent.get('tool_resources', {})
    print(f"Tool resources: {json.dumps(tr, indent=2)}")
else:
    print(f"FAILED: {resp.status_code}")
    print(resp.text)
