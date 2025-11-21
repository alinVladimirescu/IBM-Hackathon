import requests

ORCHESTRATE_URL = "https://api.au-syd.watson-orchestrate.ibm.com/v1/agents/<agentId>/runTool"
BEARER_TOKEN = "<YOUR_BEARER_TOKEN>"

payload = {
    "toolId": "send_an_email",
    "inputs": {
        "to": "jborrajof@gmail.com",
        "subject": "Hackathon Test",
        "body": "Hello! This email was sent via Orchestrate!"
    }
}

headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

response = requests.post(ORCHESTRATE_URL, json=payload, headers=headers)
print(response.json())
