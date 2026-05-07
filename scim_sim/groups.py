from scim_sim.client import make_request
from scim_sim.config import ensure_valid_config
from scim_sim.users import remove_user


def generate_group_payload(display_name):
    return {
        "displayName": display_name,
        "members": []
    }


def create_group(display_name):
    config = ensure_valid_config()
    headers = {
        "Authorization": f"Bearer {config['SCIM_AUTH_TOKEN']}",
        "Content-Type": "application/json"
    }
    response = make_request('POST', f"{config['SCIM_BASE_URL']}/Groups",
                            headers=headers, json_data=generate_group_payload(display_name))

    if 200 <= response.status_code < 300:
        group_id = response.json().get("id")
        print(f"✅ Group '{display_name}' created successfully! Group ID: {group_id}")
        return group_id
    else:
        print(f"❌ Failed to create group: {response.text}")
        return None


def delete_group(group_id):
    config = ensure_valid_config()
    headers = {
        "Authorization": f"Bearer {config['SCIM_AUTH_TOKEN']}",
        "Content-Type": "application/json"
    }

    response = make_request('GET', f"{config['SCIM_BASE_URL']}/Groups/{group_id}",
                            headers=headers)
    if 200 <= response.status_code < 300:
        members = response.json().get("members") or []

        for member in members:
            remove_user(member.get("value"))

        response = make_request('DELETE', f"{config['SCIM_BASE_URL']}/Groups/{group_id}",
                                headers=headers)
        if response.status_code == 204:
            print(f"✅ Group {group_id} and all its members deleted successfully!")
        else:
            print(f"❌ Failed to delete group: {response.text}")
    else:
        print(f"❌ Failed to fetch group details: {response.text}")


def add_user_to_group(user_id, group_id):
    config = ensure_valid_config()
    headers = {
        "Authorization": f"Bearer {config['SCIM_AUTH_TOKEN']}",
        "Content-Type": "application/json"
    }

    group_response = make_request('GET', f"{config['SCIM_BASE_URL']}/Groups/{group_id}",
                                  headers=headers)
    if group_response.status_code != 200:
        print(f"❌ Group {group_id} not found")
        return False

    members = group_response.json().get("members") or []
    members.append({"value": user_id})

    patch_payload = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
        "Operations": [{
            "op": "replace",
            "path": "members",
            "value": members
        }]
    }

    response = make_request('PATCH', f"{config['SCIM_BASE_URL']}/Groups/{group_id}",
                            headers=headers, json_data=patch_payload)

    if 200 <= response.status_code < 300:
        print(f"✅ User {user_id} added to group {group_id} successfully!")
        return True
    else:
        print(f"❌ Failed to add user to group: {response.text}")
        return False


def remove_user_from_group(user_id, group_id):
    config = ensure_valid_config()
    headers = {
        "Authorization": f"Bearer {config['SCIM_AUTH_TOKEN']}",
        "Content-Type": "application/json"
    }

    response = make_request('GET', f"{config['SCIM_BASE_URL']}/Groups/{group_id}",
                            headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch group details: {response.text}")
        return False

    members = response.json().get("members", [])
    new_members = [m for m in members if m.get("value") != user_id]

    if len(new_members) == len(members):
        print(f"❌ User {user_id} is not in group {group_id}")
        return False

    patch_payload = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
        "Operations": [{
            "op": "replace",
            "path": "members",
            "value": new_members
        }]
    }

    response = make_request('PATCH', f"{config['SCIM_BASE_URL']}/Groups/{group_id}",
                            headers=headers, json_data=patch_payload)

    if 200 <= response.status_code < 300:
        print(f"✅ User {user_id} removed from group {group_id} successfully!")
        return True
    else:
        print(f"❌ Failed to remove user from group: {response.text}")
        return False
