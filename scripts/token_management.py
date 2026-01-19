"""
Token Management Script for Medical API
Usage: python -m scripts.manage_tokens.py [command] [options]
"""

import asyncio
import argparse
import sys
from datetime import datetime, timedelta
from typing import List


from app.utils.database import db_manager
from app.utils.auth_utils import (
    generate_new_token,
    list_all_tokens,
    deactivate_token,
    activate_token,
    delete_token,
)


async def create_initial_tokens():
    """Create initial set of tokens"""
    await db_manager.connect()

    initial_tokens = [
        {
            "name": "Admin Full Access Token",
            "description": "Full administrative access to all endpoints",
            "scopes": ["read:all", "write:all", "admin"],
            "expires_in_days": None,
            "username": "admin_token",
            "full_name": "Admin Token User",
            "email": "admin@medical-api.com",
            "created_by": "system",
        },
        {
            "name": "Medical Data Read Token",
            "description": "Read access to medical data endpoints",
            "scopes": ["read:medical_data"],
            "expires_in_days": None,
            "username": "medical_api_user",
            "full_name": "Medical API User",
            "email": "api@medical-api.com",
            "created_by": "system",
        },
        {
            "name": "MCP Service Token",
            "description": "MCP service access to medical and patient data",
            "scopes": ["read:medical_data", "read:patient_data"],
            "expires_in_days": None,
            "username": "mcp_service_user",
            "full_name": "MCP Service User",
            "email": "mcp@medical-api.com",
            "created_by": "system",
        },
        {
            "name": "Demo Access Token",
            "description": "Limited demo access with short expiration",
            "scopes": ["read:medical_data"],
            "expires_in_days": None,
            "username": "demo_user",
            "full_name": "Demo User",
            "email": "demo@medical-api.com",
            "created_by": "system",
        },
    ]

    created_tokens = []
    for token_info in initial_tokens:
        try:
            token = await generate_new_token(**token_info)
            created_tokens.append((token_info["name"], token))
            print(f"✓ Created token: {token_info['name']}")
            print(f"  Token: {token}")
            print(f"  Scopes: {token_info['scopes']}")
            print(
                f"  Expires: {'Never' if not token_info['expires_in_days'] else f'{token_info['expires_in_days']} days'}"
            )
            print()
        except Exception as e:
            print(f"✗ Failed to create token '{token_info['name']}': {str(e)}")

    await db_manager.disconnect()
    return created_tokens


async def add_token(args):
    """Add a new token"""
    await db_manager.connect()

    try:
        token = await generate_new_token(
            name=args.name,
            description=args.description,
            scopes=args.scopes.split(",") if args.scopes else ["read:medical_data"],
            expires_in_days=args.expires_days,
            username=args.username,
            full_name=args.full_name,
            email=args.email,
            created_by=args.created_by or "manual",
        )

        print(f"Token created successfully!")
        print(f"Name: {args.name}")
        print(f"Token: {token}")
        print(f"Scopes: {args.scopes or 'read:medical_data'}")
        print(
            f"Expires: {'Never' if not args.expires_days else f'{args.expires_days} days'}"
        )

    except Exception as e:
        print(f"✗ Failed to create token: {str(e)}")

    await db_manager.disconnect()


async def list_tokens():
    """List all tokens"""
    await db_manager.connect()

    tokens = await list_all_tokens()

    if not tokens:
        print("No tokens found.")
        await db_manager.disconnect()
        return

    print(f"Found {len(tokens)} tokens:\n")

    for token in tokens:
        status = "Active" if token["is_active"] else "Inactive"
        expires = (
            "Never"
            if not token["expires_at"]
            else token["expires_at"].strftime("%Y-%m-%d %H:%M")
        )

        print(f"Token ID: {token['token_id']}")
        print(f"Name: {token['name']}")
        print(f"Status: {status}")
        print(f"User: {token['username']} ({token['full_name']})")
        print(f"Scopes: {', '.join(token['scopes'])}")
        print(f"Created: {token['created_at'].strftime('%Y-%m-%d %H:%M')}")
        print(f"Expires: {expires}")
        print(f"Usage: {token['use_count']} times")
        if token["last_used"]:
            print(f"Last Used: {token['last_used'].strftime('%Y-%m-%d %H:%M')}")
        print(f"Token Preview: {token['token_preview']}")
        print("-" * 50)

    await db_manager.disconnect()


async def deactivate_token_cmd(args):
    """Deactivate a token"""
    await db_manager.connect()

    success = await deactivate_token(args.token_id)

    if success:
        print(f"✓ Token {args.token_id} deactivated successfully")
    else:
        print(f"✗ Failed to deactivate token {args.token_id}")

    await db_manager.disconnect()


async def activate_token_cmd(args):
    """Activate a token"""
    await db_manager.connect()

    success = await activate_token(args.token_id)

    if success:
        print(f"✓ Token {args.token_id} activated successfully")
    else:
        print(f"✗ Failed to activate token {args.token_id}")

    await db_manager.disconnect()


async def delete_token_cmd(args):
    """Delete a token permanently"""
    await db_manager.connect()

    # Confirm deletion
    if not args.force:
        confirm = input(
            f"Are you sure you want to permanently delete token {args.token_id}? (y/N): "
        )
        if confirm.lower() != "y":
            print("Deletion cancelled")
            await db_manager.disconnect()
            return

    success = await delete_token(args.token_id)

    if success:
        print(f"✓ Token {args.token_id} deleted permanently")
    else:
        print(f"✗ Failed to delete token {args.token_id}")

    await db_manager.disconnect()


def main():
    parser = argparse.ArgumentParser(description="Manage API access tokens")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Initialize command
    init_parser = subparsers.add_parser("init", help="Create initial set of tokens")

    # Add token command
    add_parser = subparsers.add_parser("add", help="Add a new token")
    add_parser.add_argument("--name", required=True, help="Token name")
    add_parser.add_argument("--description", help="Token description")
    add_parser.add_argument(
        "--scopes",
        help="Comma-separated scopes (e.g., read:medical_data,read:patient_data)",
    )
    add_parser.add_argument(
        "--expires-days",
        type=int,
        help="Token expiration in days (omit for no expiration)",
    )
    add_parser.add_argument("--username", help="Username for the token")
    add_parser.add_argument("--full-name", help="Full name for the token user")
    add_parser.add_argument("--email", help="Email for the token user")
    add_parser.add_argument("--created-by", help="Who created this token")

    # List tokens command
    list_parser = subparsers.add_parser("list", help="List all tokens")

    # Deactivate token command
    deactivate_parser = subparsers.add_parser("deactivate", help="Deactivate a token")
    deactivate_parser.add_argument("token_id", help="Token ID to deactivate")

    # Activate token command
    activate_parser = subparsers.add_parser("activate", help="Activate a token")
    activate_parser.add_argument("token_id", help="Token ID to activate")

    # Delete token command
    delete_parser = subparsers.add_parser("delete", help="Delete a token permanently")
    delete_parser.add_argument("token_id", help="Token ID to delete")
    delete_parser.add_argument("--force", action="store_true", help="Skip confirmation")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Run the appropriate command
    if args.command == "init":
        asyncio.run(create_initial_tokens())
    elif args.command == "add":
        asyncio.run(add_token(args))
    elif args.command == "list":
        asyncio.run(list_tokens())
    elif args.command == "deactivate":
        asyncio.run(deactivate_token_cmd(args))
    elif args.command == "activate":
        asyncio.run(activate_token_cmd(args))
    elif args.command == "delete":
        asyncio.run(delete_token_cmd(args))


if __name__ == "__main__":
    main()
