import argparse
import json

from scim_sim.config import load_config, setup_config
from scim_sim.directory import show_directory
from scim_sim.groups import add_user_to_group, create_group, delete_group, remove_user_from_group
from scim_sim.users import add_user, remove_user


def main():
    parser = argparse.ArgumentParser(
        description=(
            "scim-sim — A CLI for simulating and managing a SCIM directory.\n"
            "Create and manage users and groups against any SCIM-compliant identity provider."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest='command', metavar='<command>')

    subparsers.add_parser('setup',
        help='Setup your SCIM directory configuration',
        description='Interactive setup to configure SCIM URL and authentication token.')

    subparsers.add_parser('add-user',
        help='Add user to your SCIM directory',
        description='Creates a new user with random data in the SCIM directory.')

    remove_parser = subparsers.add_parser('remove-user',
        help='Remove a user from your SCIM directory',
        description='Removes a user from the SCIM directory using their ID.')
    remove_parser.add_argument('user_id',
        help='ID of the user to remove (required)',
        metavar='USER_ID')

    subparsers.add_parser('config',
        help='View your current configuration',
        description='Displays the current SCIM configuration settings.')

    subparsers.add_parser('show',
        help='Show directory structure with groups and users',
        description='Displays a tree view of all groups and users in the directory.')

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
        print(json.dumps(load_config(), indent=2))
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


if __name__ == "__main__":
    main()
