import json
import os
import requests

from scim_sim.client import make_request

CONFIG_FILE = os.path.expanduser("~/.scim_config.json")


def is_valid_url(url):
    try:
        result = requests.utils.urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception:
        return False


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def save_config(scim_base_url, scim_auth_token):
    config = {
        "SCIM_BASE_URL": scim_base_url,
        "SCIM_AUTH_TOKEN": scim_auth_token
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    print("✅ Configuration saved successfully.")


def verify_scim_config(scim_base_url, scim_auth_token):
    headers = {
        "Authorization": f"Bearer {scim_auth_token}",
        "Content-Type": "application/json"
    }
    response = make_request('GET', f"{scim_base_url}/Users", headers=headers)

    if 200 <= response.status_code < 300:
        return True
    elif response.status_code == 401:
        print("❌ Error: Token is invalid. Please check your credentials.")
    else:
        print(f"❌ Error: Unable to verify SCIM endpoint. Response: {response.text}")
    return False


def setup_config():
    while True:
        scim_base_url = input("Enter SCIM Base URL: ").strip()

        while not is_valid_url(scim_base_url):
            print("❌ Invalid URL format. URL should start with http:// or https:// and include a domain.")
            scim_base_url = input("Enter SCIM Base URL: ").strip()

        scim_auth_token = input("Enter SCIM Auth Token: ").strip()

        if verify_scim_config(scim_base_url, scim_auth_token):
            save_config(scim_base_url, scim_auth_token)
            break
        else:
            print("❌ Setup failed. Please check your SCIM URL and token and try again.")
            break


def ensure_valid_config():
    config = load_config()
    scim_base_url = config.get("SCIM_BASE_URL", "")
    scim_auth_token = config.get("SCIM_AUTH_TOKEN", "")

    if not scim_base_url or not scim_auth_token or not verify_scim_config(scim_base_url, scim_auth_token):
        print("❌ SCIM configuration is missing or invalid. Please run the setup.")
        setup_config()
    return load_config()
