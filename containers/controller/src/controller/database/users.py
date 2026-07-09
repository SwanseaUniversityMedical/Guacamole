import logging
from typing import Dict, Optional, List
from sqlalchemy import text
from sqlalchemy.engine import Connection


def db_list_users(client: Connection) -> Dict:
    """List all users from the database."""
    logging.debug("Listing users from database")
    
    result = client.execute(
        text(
            """
            SELECT 
                e.entity_id,
                e.name as username,
                a1.attribute_value as fullname,
                a2.attribute_value as email,
                a3.attribute_value as organization,
                a4.attribute_value as role
            FROM guacamole_entity e
            LEFT JOIN guacamole_user_attribute a1 ON e.entity_id = a1.user_id AND a1.attribute_name = 'guac-full-name'
            LEFT JOIN guacamole_user_attribute a2 ON e.entity_id = a2.user_id AND a2.attribute_name = 'guac-email-address'
            LEFT JOIN guacamole_user_attribute a3 ON e.entity_id = a3.user_id AND a3.attribute_name = 'guac-organization'
            LEFT JOIN guacamole_user_attribute a4 ON e.entity_id = a4.user_id AND a4.attribute_name = 'guac-organizational-role'
            WHERE e.type = 'USER'
            """
        )
    )
    
    users = {}
    for row in result:
        users[row.username] = {
            "username": row.username,
            "attributes": {
                "guac-full-name": row.fullname or "",
                "guac-email-address": row.email or "",
                "guac-organization": row.organization or "",
                "guac-organizational-role": row.role or ""
            }
        }
    
    return users


def db_get_user(client: Connection, username: str) -> Optional[Dict]:
    """Get a specific user from the database."""
    logging.debug(f"Getting user {username=}")
    
    result = client.execute(
        text(
            """
            SELECT 
                e.entity_id,
                e.name as username,
                a1.attribute_value as fullname,
                a2.attribute_value as email,
                a3.attribute_value as organization,
                a4.attribute_value as role
            FROM guacamole_entity e
            LEFT JOIN guacamole_user_attribute a1 ON e.entity_id = a1.user_id AND a1.attribute_name = 'guac-full-name'
            LEFT JOIN guacamole_user_attribute a2 ON e.entity_id = a2.user_id AND a2.attribute_name = 'guac-email-address'
            LEFT JOIN guacamole_user_attribute a3 ON e.entity_id = a3.user_id AND a3.attribute_name = 'guac-organization'
            LEFT JOIN guacamole_user_attribute a4 ON e.entity_id = a4.user_id AND a4.attribute_name = 'guac-organizational-role'
            WHERE e.type = 'USER' AND e.name = :username
            """
        ),
        parameters={"username": username}
    )
    
    row = result.fetchone()
    if not row:
        return None
    
    return {
        "username": row.username,
        "attributes": {
            "guac-full-name": row.fullname or "",
            "guac-email-address": row.email or "",
            "guac-organization": row.organization or "",
            "guac-organizational-role": row.role or ""
        }
    }


def db_create_user(
    client: Connection,
    username: str,
    fullname: str,
    email: str,
    organization: str,
    role: str
):
    """Create a new user in the database."""
    logging.info(f"Creating user {username=}")
    
    # Create entity
    client.execute(
        text(
            "INSERT INTO guacamole_entity (name, type) "
            "VALUES (:username, 'USER') "
            "ON CONFLICT DO NOTHING;"
        ),
        parameters={"username": username}
    )
    
    # Create user with no password (LDAP authentication)
    client.execute(
        text(
            "INSERT INTO guacamole_user (entity_id, password_hash, password_salt, password_date) "
            "SELECT entity_id, NULL, NULL, NULL "
            "FROM guacamole_entity WHERE name = :username AND type = 'USER' "
            "ON CONFLICT DO NOTHING;"
        ),
        parameters={"username": username}
    )
    
    # Set user attributes
    _set_user_attributes(client, username, fullname, email, organization, role)


def db_update_user(
    client: Connection,
    username: str,
    fullname: str,
    email: str,
    organization: str,
    role: str
):
    """Update an existing user in the database."""
    logging.info(f"Updating user {username=}")
    _set_user_attributes(client, username, fullname, email, organization, role)


def _set_user_attributes(
    client: Connection,
    username: str,
    fullname: str,
    email: str,
    organization: str,
    role: str
):
    """Set user attributes."""
    attributes = [
        ("guac-full-name", fullname),
        ("guac-email-address", email),
        ("guac-organization", organization),
        ("guac-organizational-role", role)
    ]
    
    for attr_name, attr_value in attributes:
        client.execute(
            text(
                """
                INSERT INTO guacamole_user_attribute (user_id, attribute_name, attribute_value)
                SELECT entity_id, :attr_name, :attr_value
                FROM guacamole_entity 
                WHERE name = :username AND type = 'USER'
                ON CONFLICT (user_id, attribute_name) 
                DO UPDATE SET attribute_value = excluded.attribute_value;
                """
            ),
            parameters={
                "username": username,
                "attr_name": attr_name,
                "attr_value": attr_value
            }
        )


def db_delete_user(client: Connection, username: str):
    """Delete a user from the database."""
    logging.info(f"Deleting user {username=}")
    
    # Get entity_id first
    result = client.execute(
        text("SELECT entity_id FROM guacamole_entity WHERE name = :username AND type = 'USER'"),
        parameters={"username": username}
    )
    row = result.fetchone()
    if not row:
        return
    
    entity_id = row.entity_id
    
    # Delete user attributes
    client.execute(
        text("DELETE FROM guacamole_user_attribute WHERE user_id = :entity_id"),
        parameters={"entity_id": entity_id}
    )
    
    # Delete user permissions
    client.execute(
        text("DELETE FROM guacamole_connection_permission WHERE entity_id = :entity_id"),
        parameters={"entity_id": entity_id}
    )
    
    # Delete user
    client.execute(
        text("DELETE FROM guacamole_user WHERE entity_id = :entity_id"),
        parameters={"entity_id": entity_id}
    )
    
    # Delete entity
    client.execute(
        text("DELETE FROM guacamole_entity WHERE entity_id = :entity_id"),
        parameters={"entity_id": entity_id}
    )


def db_user_exists(client: Connection, username: str) -> bool:
    """Check if a user exists in the database."""
    result = client.execute(
        text("SELECT 1 FROM guacamole_entity WHERE name = :username AND type = 'USER'"),
        parameters={"username": username}
    )
    return result.fetchone() is not None


def db_create_or_update_user(
    client: Connection,
    username: str,
    fullname: str,
    email: str,
    organization: str,
    role: str
):
    """Create or update a user in the database."""
    existing_user = db_get_user(client, username)
    
    if existing_user:
        # Check if update is needed
        needs_update = any([
            (fullname != existing_user["attributes"]["guac-full-name"]),
            (email != existing_user["attributes"]["guac-email-address"]),
            (organization != existing_user["attributes"]["guac-organization"]),
            (role != existing_user["attributes"]["guac-organizational-role"])
        ])
        
        if needs_update:
            db_update_user(client, username, fullname, email, organization, role)
    else:
        db_create_user(client, username, fullname, email, organization, role)
