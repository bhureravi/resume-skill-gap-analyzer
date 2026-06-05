import requests

payload = {
    "model": "llama3.2:1b",
    "prompt": "Say hello in one short sentence.",
    "stream": False,
    "format": "json"
}

response = requests.post(
    "http://localhost:11434/api/generate",
    json=payload,
    timeout=120
)

response.raise_for_status()
print(response.json()["response"])