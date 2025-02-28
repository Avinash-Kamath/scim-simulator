import requests
import random
import string
import argparse
import json
import os
import sys
from faker import Faker
import subprocess

DEBUG = False


fake = Faker()

CONFIG_FILE = os.path.expanduser("~/.scim_config.json")

def check_and_install_dependencies():
    """Checks for required dependencies and installs them if missing."""
    required_packages = ["requests", "faker"]
    try:
        for package in required_packages:
            __import__(package)
    except ImportError:
        python_cmd = "python3" if sys.version_info.major == 3 else "python"
        print("Installing required dependencies...")
        subprocess.check_call([python_cmd, "-m", "pip", "install"] + required_packages)

def check_python_installed():
    """Checks if Python is installed and prompts the user to install if missing."""
    if not sys.executable:
        print("Python is not installed. Please install Python and try again.")
        sys.exit(1)

def load_config():
    """Loads SCIM configuration from a config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(scim_base_url, scim_auth_token):
    """Saves SCIM configuration to a config file."""
    config = {
        "SCIM_BASE_URL": scim_base_url,
        "SCIM_AUTH_TOKEN": scim_auth_token
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    print("✅ Configuration saved successfully.")

def verify_scim_config(scim_base_url, scim_auth_token):
    """Verifies SCIM configuration by making a GET request to /Users."""
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

def is_valid_url(url):
    """Validates if the given URL has a proper format."""
    try:
        result = requests.utils.urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception:
        return False

def setup_config():
    """Interactive setup for SCIM configuration."""
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
    """Ensures a valid SCIM configuration exists before executing commands."""
    config = load_config()
    scim_base_url = config.get("SCIM_BASE_URL", "")
    scim_auth_token = config.get("SCIM_AUTH_TOKEN", "")
    
    if not scim_base_url or not scim_auth_token or not verify_scim_config(scim_base_url, scim_auth_token):
        print("❌ SCIM configuration is missing or invalid. Please run the setup.")
        setup_config()
    return load_config()

def generate_random_payload():
    """Generates a minimal SCIM user payload with random data."""
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
    """Adds a user to the SCIM directory."""
    config = ensure_valid_config()
    headers = {
        "Authorization": f"Bearer {config['SCIM_AUTH_TOKEN']}",
        "Content-Type": "application/json"
    }
    user_payload = generate_random_payload()
    response = make_request('POST', f"{config['SCIM_BASE_URL']}/Users", 
                          headers=headers, json_data=user_payload)
    
    if 200 <= response.status_code < 300:
        user_id = response.json().get("id")
        print(f"✅ User created successfully! User ID: {user_id}")
        return user_id
    else:
        print(f"❌ Failed to create user: {response.text}")
        return None

def remove_user(user_id):
    """Removes a user from the SCIM directory."""
    config = ensure_valid_config()
    headers = {
        "Authorization": f"Bearer {config['SCIM_AUTH_TOKEN']}",
        "Content-Type": "application/json"
    }
    response = requests.delete(f"{config['SCIM_BASE_URL']}/Users/{user_id}", headers=headers)
    
    if response.status_code == 204:
        print(f"✅ User {user_id} deleted successfully!")
    else:
        print(f"❌ Failed to delete user: {response.text}")

def show_directory():
    """Shows the SCIM directory structure with groups and users."""
    config = ensure_valid_config()
    headers = {
        "Authorization": f"Bearer {config['SCIM_AUTH_TOKEN']}",
        "Content-Type": "application/json"
    }
    
    # Get all groups (list operation)
    groups_response = make_request('GET', f"{config['SCIM_BASE_URL']}/Groups", headers=headers)
    # Get all users
    users_response = make_request('GET', f"{config['SCIM_BASE_URL']}/Users", headers=headers)
    
    if groups_response.status_code < 200 or groups_response.status_code >= 300:
        print(f"❌ Failed to fetch groups: {groups_response.text}")
        return
    if users_response.status_code < 200 or users_response.status_code >= 300:
        print(f"❌ Failed to fetch users: {users_response.text}")
        return
    
    groups = groups_response.json().get("Resources", [])
    users = users_response.json().get("Resources", [])
    
    # Create a map of user IDs to usernames for quick lookup
    user_map = {user.get('id'): user.get('userName') for user in users}
    
    # Create a map of users to their groups
    user_groups = {}
    
    # Find the longest username for alignment
    all_usernames = [user.get('userName', 'N/A') for user in users]
    max_username_length = max(len(name) for name in all_usernames) if all_usernames else 0
    
    print("📂 Directory")
    
    # Print groups first
    if groups:
        print("├── 👥 Groups")
        for i, group in enumerate(groups):
            group_id = group.get('id')
            # Get detailed group info including members
            group_detail_response = make_request('GET', 
                f"{config['SCIM_BASE_URL']}/Groups/{group_id}", 
                headers=headers
            )
            
            if group_detail_response.status_code < 200 or group_detail_response.status_code >= 300:
                print(f"❌ Failed to fetch group details: {group_detail_response.text}")
                continue
                
            group_detail = group_detail_response.json()
            prefix = "│   └──" if i == len(groups) - 1 else "│   ├──"
            group_name = group_detail.get('displayName', 'N/A')
            print(f"{prefix} {group_name} │ ID: {group_id}")
            
            # Print group members and update user_groups map
            members = group_detail.get('members', [])
            if members:
                member_prefix = "│   " if i < len(groups) - 1 else "    "
                for j, member in enumerate(members):
                    member_id = member.get('value')
                    if member_id not in user_groups:
                        user_groups[member_id] = []
                    user_groups[member_id].append(group_name)
                    
                    username = user_map.get(member_id, 'N/A')
                    sub_prefix = "└──" if j == len(members) - 1 else "├──"
                    padded_username = username.ljust(max_username_length)
                    print(f"{member_prefix}    {sub_prefix} 👤 {padded_username} │ ID: {member_id}")
            
            # Add spacing between groups unless it's the last group
            if i < len(groups) - 1:
                print("│")
    
    # Print ungrouped users with spacing
    ungrouped_users = [user for user in users if user.get('id') not in user_groups]
    if ungrouped_users:
        # Add spacing before ungrouped users section if there were groups
        if groups:
            print()
        print("└── 👤 Ungrouped Users")
        for i, user in enumerate(ungrouped_users):
            prefix = "    └──" if i == len(ungrouped_users) - 1 else "    ├──"
            username = user.get('userName', 'N/A')
            user_id = user.get('id', 'N/A')
            padded_username = username.ljust(max_username_length)
            print(f"{prefix} {padded_username} │ ID: {user_id}")
    
    if not groups and not users:
        print("└── (empty)")

def generate_group_payload(display_name):
    """Generates a SCIM group payload."""
    return {
        "displayName": display_name,
        "members": []
    }

def create_group(display_name):
    """Creates a new group in the SCIM directory."""
    config = ensure_valid_config()
    headers = {
        "Authorization": f"Bearer {config['SCIM_AUTH_TOKEN']}",
        "Content-Type": "application/json"
    }
    group_payload = generate_group_payload(display_name)
    response = requests.post(f"{config['SCIM_BASE_URL']}/Groups", json=group_payload, headers=headers)
    
    if 200 <= response.status_code < 300:
        group_id = response.json().get("id")
        print(f"✅ Group '{display_name}' created successfully! Group ID: {group_id}")
        return group_id
    else:
        print(f"❌ Failed to create group: {response.text}")
        return None

def delete_group(group_id):
    """Deletes a group and all its members from the SCIM directory."""
    config = ensure_valid_config()
    headers = {
        "Authorization": f"Bearer {config['SCIM_AUTH_TOKEN']}",
        "Content-Type": "application/json"
    }
    
    # First get group details to find members
    response = requests.get(f"{config['SCIM_BASE_URL']}/Groups/{group_id}", headers=headers)
    if 200 <= response.status_code < 300:
        group = response.json()
        members = group.get("members", [])
        
        # Delete all members first
        for member in members:
            member_id = member.get("value")
            remove_user(member_id)
        
        # Then delete the group
        response = requests.delete(f"{config['SCIM_BASE_URL']}/Groups/{group_id}", headers=headers)
        if response.status_code == 204:
            print(f"✅ Group {group_id} and all its members deleted successfully!")
        else:
            print(f"❌ Failed to delete group: {response.text}")
    else:
        print(f"❌ Failed to fetch group details: {response.text}")

def add_user_to_group(user_id, group_id):
    """Adds a user to a group."""
    config = ensure_valid_config()
    headers = {
        "Authorization": f"Bearer {config['SCIM_AUTH_TOKEN']}",
        "Content-Type": "application/json"
    }
    
    # First check if group exists
    group_response = make_request('GET', f"{config['SCIM_BASE_URL']}/Groups/{group_id}", headers=headers)
    if group_response.status_code != 200:
        print(f"❌ Group {group_id} not found")
        return False
    
    group = group_response.json()
    members = group.get("members")
    members = [] if members == None else members
        
    
    # Add new member
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
    """Removes a user from a group."""
    config = ensure_valid_config()
    headers = {
        "Authorization": f"Bearer {config['SCIM_AUTH_TOKEN']}",
        "Content-Type": "application/json"
    }
    
    # Get current group members
    response = requests.get(f"{config['SCIM_BASE_URL']}/Groups/{group_id}", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch group details: {response.text}")
        return False
    
    group = response.json()
    members = group.get("members", [])
    
    # Remove member
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
    
    response = requests.patch(f"{config['SCIM_BASE_URL']}/Groups/{group_id}", 
                            json=patch_payload, headers=headers)
    
    if 200 <= response.status_code < 300:
        print(f"✅ User {user_id} removed from group {group_id} successfully!")
        return True
    else:
        print(f"❌ Failed to remove user from group: {response.text}")
        return False

def debug_request(method, url, headers=None, data=None, response=None):
    """Pretty prints request and response details when DEBUG is True."""
    if not DEBUG:
        return
    
    print("\n🔍 DEBUG Information:")
    print("├── Request:")
    print(f"│   ├── Method: {method}")
    print(f"│   ├── URL: {url}")
    if headers:
        print("│   ├── Headers:")
        for key, value in headers.items():
            # Mask the authorization token
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
        except:
            print(f"    └── Body: {response.text}")
    print()

def make_request(method, url, headers=None, json_data=None):
    response = requests.request(method, url, headers=headers, json=json_data)
    debug_request(method, url, headers, json_data, response)
    return response

def main():
    parser = argparse.ArgumentParser(
        description="SCIM User Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    subparsers.add_parser('setup', 
        help='Setup your SCIM directory configuration',
        description='Interactive setup to configure SCIM URL and authentication token.')
    
    # Add user command
    subparsers.add_parser('add-user', 
        help='Add user to your SCIM directory',
        description='Creates a new user with random data in the SCIM directory.')
    
    # Remove user command
    remove_parser = subparsers.add_parser('remove-user', 
        help='Remove a user from your SCIM directory',
        description='Removes a user from the SCIM directory using their ID.')
    remove_parser.add_argument('user_id', 
        help='ID of the user to remove (required)',
        metavar='USER_ID')
    
    # Config command
    subparsers.add_parser('config', 
        help='View your current configuration',
        description='Displays the current SCIM configuration settings.')
    
    # Show command
    subparsers.add_parser('show', 
        help='Show directory structure with groups and users',
        description='Displays a tree view of all groups and users in the directory.')
    
    # Group management commands
    create_group_parser = subparsers.add_parser('create-group', 
        help='Create a new group',
        description='Creates a new empty group in the SCIM directory.')
    create_group_parser.add_argument('display_name', 
        help='Display name for the group (required)',
        metavar='GROUP_NAME')
    
    delete_group_parser = subparsers.add_parser('delete-group', 
        help='Delete a group and all its members',
        description='Deletes a group and all users that belong to it.')
    delete_group_parser.add_argument('group_id', 
        help='ID of the group to delete (required)',
        metavar='GROUP_ID')
    
    add_to_group_parser = subparsers.add_parser('add-to-group', 
        help='Add a user to a group',
        description='Adds an existing user to an existing group.')
    add_to_group_parser.add_argument('user_id', 
        help='ID of the user to add (required)',
        metavar='USER_ID')
    add_to_group_parser.add_argument('group_id', 
        help='ID of the group to add the user to (required)',
        metavar='GROUP_ID')
    
    remove_from_group_parser = subparsers.add_parser('remove-from-group', 
        help='Remove a user from a group',
        description='Removes a user from a group without deleting the user.')
    remove_from_group_parser.add_argument('user_id', 
        help='ID of the user to remove (required)',
        metavar='USER_ID')
    remove_from_group_parser.add_argument('group_id', 
        help='ID of the group to remove the user from (required)',
        metavar='GROUP_ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "setup":
        setup_config()
    elif args.command == "config":
        config = load_config()
        print(json.dumps(config, indent=2))
    elif args.command == "add-user":
        add_user()
    elif args.command == "remove-user":
        remove_user(args.user_id)
    elif args.command == "show":
        show_directory()
    elif args.command == "create-group":
        create_group(args.display_name)
    elif args.command == "delete-group":
        delete_group(args.group_id)
    elif args.command == "add-to-group":
        add_user_to_group(args.user_id, args.group_id)
    elif args.command == "remove-from-group":
        remove_user_from_group(args.user_id, args.group_id)
    
    if DEBUG:
        show_directory()

if __name__ == "__main__":
    main()
