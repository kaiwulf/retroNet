"""Invite codes. retroNet is invite-only: signing up requires an unused code."""
import secrets

import click
from flask.cli import with_appcontext

from retroApp.models.db import get_db


def create_invite(created_by=None):
    """Create a new, unused invite code and return it.

    Args:
        created_by: id of the user handing out the invite, or None for
            invites made by the site admin from the command line.
    """
    code = secrets.token_urlsafe(8)
    db = get_db()
    db.execute(
        "INSERT INTO invite (invite_code, created_by) VALUES (?, ?)",
        (code, created_by),
    )
    db.commit()
    return code
# JOLfgPoF0z4

def claim_invite(code, user_id):
    """Mark an invite as used by user_id.

    Returns True if the code was valid and unused, False otherwise.
    Does not commit: the caller commits it together with the new user,
    so either both are saved or neither is.
    """
    db = get_db()
    cursor = db.execute(
        "UPDATE invite SET used_by = ?, used_at = CURRENT_TIMESTAMP"
        " WHERE invite_code = ? AND used_by IS NULL AND is_active = 1",
        (user_id, code),
    )
    return cursor.rowcount == 1

@click.command('create-invite')
@with_appcontext
@click.option('--count', default=1, help='How many invite codes to create.')
def create_invite_command(count):
    """Print new invite codes."""
    for _ in range(count):
        click.echo(create_invite())
