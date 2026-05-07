# SCIM Directory Simulator CLI

A command-line tool for simulating and managing a [SCIM](https://scim.cloud) (System for Cross-domain Identity Management) directory. This tool allows you to create and manage users and groups, simulating a real SCIM-compliant identity provider.

## Installation

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv tool install scim-sim
```

**First-time setup:** If `scim-sim` is not found after installing, run:

```bash
uv tool update-shell
```

Then restart your terminal. This is a one-time step that adds `~/.local/bin` to your PATH so all uv-installed tools are available globally.

Alternatively, via Homebrew:

```bash
brew tap Avinash-Kamath/brews
brew install scim-sim
```

## Configuration

Before using the tool, you need to set up your SCIM configuration:

```bash
scim-sim setup
```

This will prompt you for:
- SCIM Base URL - The endpoint of your SCIM service (e.g., https://api.example.com/scim/v2)
- SCIM Auth Token - Your authentication token

Configuration is stored in `~/.scim_config.json`. You can view your current configuration with:

```bash
scim-sim config
```

## Commands

### User Management

```bash
# Add a new user (generates random user data)
scim-sim add-user

# Remove a user
scim-sim remove-user <user-id>
```

### Group Management

```bash
# Create a new group
scim-sim create-group "Engineering Team"

# Delete a group and its members
scim-sim delete-group <group-id>

# Add user to group
scim-sim add-to-group <user-id> <group-id>

# Remove user from group
scim-sim remove-from-group <user-id> <group-id>
```

### Directory Visualization

```bash
# Show complete directory structure
scim-sim show
```

This will display a tree view of your directory structure, showing all groups and users.

Example output:
```
📂 Directory
├── 👥 Groups
│   ├── Engineering Team │ ID: dirgrp_1234567890123456
│   │    ├── 👤 avinash.kamath@example.com │ ID: dirusr_8913202356420102
│   │    └── 👤 srini.k@example.com │ ID: dirusr_4123456789012345
│   │
│   └── Product Team │ ID: dirgrp_6789012345678901
└── 👤 Ungrouped Users
    └── ravi@example.com │ ID: dirusr_6789012345678901
```

## Available Commands

- `setup` - Configure SCIM settings
- `config` - View current configuration
- `add-user` - Create a new user
- `remove-user` - Delete a user
- `show` - Display directory structure
- `create-group` - Create a new group
- `delete-group` - Delete a group and its members
- `add-to-group` - Add user to group
- `remove-from-group` - Remove user from group