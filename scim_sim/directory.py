from scim_sim.client import make_request
from scim_sim.config import ensure_valid_config


def show_directory():
    config = ensure_valid_config()
    headers = {
        "Authorization": f"Bearer {config['SCIM_AUTH_TOKEN']}",
        "Content-Type": "application/json"
    }

    groups_response = make_request('GET', f"{config['SCIM_BASE_URL']}/Groups", headers=headers)
    users_response = make_request('GET', f"{config['SCIM_BASE_URL']}/Users", headers=headers)

    if groups_response.status_code < 200 or groups_response.status_code >= 300:
        print(f"❌ Failed to fetch groups: {groups_response.text}")
        return
    if users_response.status_code < 200 or users_response.status_code >= 300:
        print(f"❌ Failed to fetch users: {users_response.text}")
        return

    groups = groups_response.json().get("Resources", [])
    users = users_response.json().get("Resources", [])

    user_map = {user.get('id'): user.get('userName') for user in users}
    user_groups = {}

    all_usernames = [user.get('userName', 'N/A') for user in users]
    max_username_length = max(len(name) for name in all_usernames) if all_usernames else 0

    print("📂 Directory")

    if groups:
        print("├── 👥 Groups")
        for i, group in enumerate(groups):
            group_id = group.get('id')
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

            if i < len(groups) - 1:
                print("│")

    ungrouped_users = [user for user in users if user.get('id') not in user_groups]
    if ungrouped_users:
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
