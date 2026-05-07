import random
import string

from faker import Faker

from scim_sim.client import make_request
from scim_sim.config import ensure_valid_config

fake = Faker()


def generate_random_payload():
    return {
        "active": True,
        "name": {
            "givenName": fake.first_name(),
            "familyName": fake.last_name(),
            "formatted": fake.first_name(),
            "middleName": fake.first_name(),
            "honorificPrefix": fake.prefix(),
            "honorificSuffix": fake.suffix()
        },
        "nickName": ''.join(random.choices(string.ascii_uppercase, k=12)),
        "userName": fake.email(),
        "userType": ''.join(random.choices(string.ascii_uppercase, k=12))
    }


def add_user():
    config = ensure_valid_config()
    headers = {
        "Authorization": f"Bearer {config['SCIM_AUTH_TOKEN']}",
        "Content-Type": "application/json"
    }
    response = make_request('POST', f"{config['SCIM_BASE_URL']}/Users",
                            headers=headers, json_data=generate_random_payload())

    if 200 <= response.status_code < 300:
        user_id = response.json().get("id")
        print(f"✅ User created successfully! User ID: {user_id}")
        return user_id
    else:
        print(f"❌ Failed to create user: {response.text}")
        return None


def remove_user(user_id):
    config = ensure_valid_config()
    headers = {
        "Authorization": f"Bearer {config['SCIM_AUTH_TOKEN']}",
        "Content-Type": "application/json"
    }
    response = make_request('DELETE', f"{config['SCIM_BASE_URL']}/Users/{user_id}",
                            headers=headers)

    if response.status_code == 204:
        print(f"✅ User {user_id} deleted successfully!")
    else:
        print(f"❌ Failed to delete user: {response.text}")
