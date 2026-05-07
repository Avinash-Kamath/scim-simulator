import json
import requests

DEBUG = False


def debug_request(method, url, headers=None, data=None, response=None):
    if not DEBUG:
        return

    print("\n🔍 DEBUG Information:")
    print("├── Request:")
    print(f"│   ├── Method: {method}")
    print(f"│   ├── URL: {url}")
    if headers:
        print("│   ├── Headers:")
        for key, value in headers.items():
            if key.lower() == 'authorization':
                value = f"{value[:15]}...{value[-5:]}"
            print(f"│   │   ├── {key}: {value}")
    if data:
        print("│   └── Payload:")
        print("│       ", json.dumps(data, indent=2).replace('\n', '\n│       '))

    if response:
        print("└── Response:")
        print(f"    ├── Status: {response.status_code}")
        print(f"    ├── Elapsed: {response.elapsed.total_seconds():.2f}s")
        try:
            resp_data = response.json()
            print("    └── Body:")
            print("        ", json.dumps(resp_data, indent=2).replace('\n', '\n        '))
        except Exception:
            print(f"    └── Body: {response.text}")
    print()


def make_request(method, url, headers=None, json_data=None):
    response = requests.request(method, url, headers=headers, json=json_data)
    debug_request(method, url, headers, json_data, response)
    return response
