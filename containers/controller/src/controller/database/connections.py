import logging
from typing import Dict, Optional, List
from sqlalchemy import text
from sqlalchemy.engine import Connection


def db_list_connections(client: Connection) -> Dict:
    """List all connections from the database."""
    logging.debug("Listing connections from database")
    
    result = client.execute(
        text(
            """
            SELECT 
                connection_id,
                connection_name,
                protocol,
                parent_id
            FROM guacamole_connection
            """
        )
    )
    
    connections = {}
    for row in result:
        connections[str(row.connection_id)] = {
            "identifier": str(row.connection_id),
            "name": row.connection_name,
            "protocol": row.protocol,
            "parentIdentifier": str(row.parent_id) if row.parent_id else None
        }
    
    return connections


def db_get_connection_by_name(client: Connection, conn_name: str) -> Optional[int]:
    """Get connection ID by name."""
    logging.debug(f"Getting connection by name {conn_name=}")
    
    result = client.execute(
        text("SELECT connection_id FROM guacamole_connection WHERE connection_name = :conn_name"),
        parameters={"conn_name": conn_name}
    )
    
    row = result.fetchone()
    return row.connection_id if row else None


def db_get_connection(client: Connection, conn_id: int) -> Optional[Dict]:
    """Get a specific connection from the database."""
    logging.debug(f"Getting connection {conn_id=}")
    
    result = client.execute(
        text(
            """
            SELECT 
                connection_id,
                connection_name,
                protocol,
                parent_id
            FROM guacamole_connection 
            WHERE connection_id = :conn_id
            """
        ),
        parameters={"conn_id": conn_id}
    )
    
    row = result.fetchone()
    if not row:
        return None
    
    return {
        "identifier": str(row.connection_id),
        "name": row.connection_name,
        "protocol": row.protocol,
        "parentIdentifier": str(row.parent_id) if row.parent_id else None
    }


def db_create_connection(
    client: Connection,
    name: str,
    protocol: str,
    parent: str,
    hostname: str,
    port: int
) -> int:
    """Create a new connection in the database."""
    logging.info(f"Creating connection {name=}")
    
    # Get parent_id (ROOT is typically NULL or a specific group)
    parent_id = None
    if parent != "ROOT":
        parent_result = client.execute(
            text("SELECT connection_group_id FROM guacamole_connection_group WHERE connection_group_name = :parent"),
            parameters={"parent": parent}
        )
        parent_row = parent_result.fetchone()
        if parent_row:
            parent_id = parent_row.connection_group_id
    
    # Insert connection
    result = client.execute(
        text(
            """
            INSERT INTO guacamole_connection (connection_name, protocol, parent_id)
            VALUES (:name, :protocol, :parent_id)
            RETURNING connection_id
            """
        ),
        parameters={
            "name": name,
            "protocol": protocol,
            "parent_id": parent_id
        }
    )
    
    conn_id = result.fetchone().connection_id
    
    # Set connection parameters
    _set_connection_parameters(client, conn_id, hostname, port)
    
    return conn_id


def db_update_connection(
    client: Connection,
    conn_id: int,
    name: str,
    protocol: str,
    parent: str,
    hostname: str,
    port: int
):
    """Update an existing connection in the database."""
    logging.info(f"Updating connection {name=} {conn_id=}")
    
    # Get parent_id
    parent_id = None
    if parent != "ROOT":
        parent_result = client.execute(
            text("SELECT connection_group_id FROM guacamole_connection_group WHERE connection_group_name = :parent"),
            parameters={"parent": parent}
        )
        parent_row = parent_result.fetchone()
        if parent_row:
            parent_id = parent_row.connection_group_id
    
    # Update connection
    client.execute(
        text(
            """
            UPDATE guacamole_connection 
            SET connection_name = :name, protocol = :protocol, parent_id = :parent_id
            WHERE connection_id = :conn_id
            """
        ),
        parameters={
            "conn_id": conn_id,
            "name": name,
            "protocol": protocol,
            "parent_id": parent_id
        }
    )
    
    # Update connection parameters
    _set_connection_parameters(client, conn_id, hostname, port)


def _set_connection_parameters(client: Connection, conn_id: int, hostname: str, port: int):
    """Set connection parameters."""
    parameters = [
        ("hostname", hostname),
        ("port", str(port))
    ]
    
    for param_name, param_value in parameters:
        client.execute(
            text(
                """
                INSERT INTO guacamole_connection_parameter (connection_id, parameter_name, parameter_value)
                VALUES (:conn_id, :param_name, :param_value)
                ON CONFLICT (connection_id, parameter_name) 
                DO UPDATE SET parameter_value = excluded.parameter_value;
                """
            ),
            parameters={
                "conn_id": conn_id,
                "param_name": param_name,
                "param_value": param_value
            }
        )


def db_delete_connection(client: Connection, conn_id: int):
    """Delete a connection from the database."""
    logging.info(f"Deleting connection {conn_id=}")
    
    # Delete connection parameters
    client.execute(
        text("DELETE FROM guacamole_connection_parameter WHERE connection_id = :conn_id"),
        parameters={"conn_id": conn_id}
    )
    
    # Delete connection permissions
    client.execute(
        text("DELETE FROM guacamole_connection_permission WHERE connection_id = :conn_id"),
        parameters={"conn_id": conn_id}
    )
    
    # Delete connection
    client.execute(
        text("DELETE FROM guacamole_connection WHERE connection_id = :conn_id"),
        parameters={"conn_id": conn_id}
    )


def db_create_or_update_connection(
    client: Connection,
    name: str,
    protocol: str,
    parent: str,
    hostname: str,
    port: int
) -> int:
    """Create or update a connection in the database."""
    existing_conn_id = db_get_connection_by_name(client, name)
    
    if existing_conn_id:
        db_update_connection(client, existing_conn_id, name, protocol, parent, hostname, port)
        return existing_conn_id
    else:
        return db_create_connection(client, name, protocol, parent, hostname, port)


def db_create_user_connection(
    client: Connection,
    username: str,
    conn_id: int
):
    """Grant a user READ permission to a connection."""
    logging.info(f"Creating user connection {username=} {conn_id=}")
    
    client.execute(
        text(
            """
            INSERT INTO guacamole_connection_permission (entity_id, connection_id, permission)
            SELECT e.entity_id, :conn_id, 'READ'
            FROM guacamole_entity e
            WHERE e.name = :username AND e.type = 'USER'
            ON CONFLICT DO NOTHING;
            """
        ),
        parameters={
            "username": username,
            "conn_id": conn_id
        }
    )


def db_delete_user_connection(
    client: Connection,
    username: str,
    conn_id: int
):
    """Revoke a user's READ permission to a connection."""
    logging.info(f"Deleting user connection {username=} {conn_id=}")
    
    client.execute(
        text(
            """
            DELETE FROM guacamole_connection_permission 
            WHERE connection_id = :conn_id 
            AND entity_id = (
                SELECT entity_id FROM guacamole_entity 
                WHERE name = :username AND type = 'USER'
            )
            """
        ),
        parameters={
            "username": username,
            "conn_id": conn_id
        }
    )


def db_list_connection_users(client: Connection, conn_id: int) -> Dict:
    """List all users with READ permission to a connection."""
    logging.debug(f"Listing users for connection {conn_id=}")
    
    result = client.execute(
        text(
            """
            SELECT 
                e.name as username,
                a1.attribute_value as fullname,
                a2.attribute_value as email,
                a3.attribute_value as organization,
                a4.attribute_value as role
            FROM guacamole_entity e
            JOIN guacamole_connection_permission cp ON e.entity_id = cp.entity_id
            LEFT JOIN guacamole_user_attribute a1 ON e.entity_id = a1.user_id AND a1.attribute_name = 'guac-full-name'
            LEFT JOIN guacamole_user_attribute a2 ON e.entity_id = a2.user_id AND a2.attribute_name = 'guac-email-address'
            LEFT JOIN guacamole_user_attribute a3 ON e.entity_id = a3.user_id AND a3.attribute_name = 'guac-organization'
            LEFT JOIN guacamole_user_attribute a4 ON e.entity_id = a4.user_id AND a4.attribute_name = 'guac-organizational-role'
            WHERE e.type = 'USER' 
            AND cp.connection_id = :conn_id 
            AND cp.permission = 'READ'
            """
        ),
        parameters={"conn_id": conn_id}
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
