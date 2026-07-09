import logging
from sqlalchemy.engine import Connection

from .users import (
    db_list_users,
    db_get_user,
    db_create_user,
    db_update_user,
    db_delete_user,
    db_create_or_update_user,
    db_user_exists
)
from .connections import (
    db_list_connections,
    db_get_connection_by_name,
    db_get_connection,
    db_create_connection,
    db_update_connection,
    db_delete_connection,
    db_create_or_update_connection,
    db_create_user_connection,
    db_delete_user_connection,
    db_list_connection_users
)


class DatabaseUserDoesNotExistError(Exception):
    """Exception raised when a user does not exist in the database."""
    pass


class DatabaseConnectionDoesNotExistError(Exception):
    """Exception raised when a connection does not exist in the database."""
    pass


class Database:
    """Database wrapper to replace API calls with direct database operations."""

    def __init__(self, client: Connection, username: str):
        self.client = client
        self.username = username  # Service account username
        # Start a transaction for all operations
        if not self.client.in_transaction():
            self._transaction = self.client.begin()
        else:
            self._transaction = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._transaction is not None:
            if exc_type is None:
                self._transaction.commit()
            else:
                self._transaction.rollback()

    def list_users(self):
        """List all users."""
        return db_list_users(self.client)

    def get_user(self, username: str):
        """Get a specific user."""
        user = db_get_user(self.client, username)
        if not user:
            raise DatabaseUserDoesNotExistError(f"User {username} does not exist")
        return user

    def create_user(
        self,
        username: str,
        fullname: str,
        email: str,
        organization: str,
        role: str
    ):
        """Create a new user."""
        if self.username == username:
            raise ValueError(f"Trying to create user with same name as service account! {self.username} {username}")

        logging.info(f"Creating user {username=}")
        db_create_user(self.client, username, fullname, email, organization, role)

    def update_user(
        self,
        username: str,
        fullname: str,
        email: str,
        organization: str,
        role: str
    ):
        """Update an existing user."""
        if self.username == username:
            raise ValueError(f"Trying to update user with same name as service account! {self.username} {username}")

        logging.info(f"Updating user {username=}")
        db_update_user(self.client, username, fullname, email, organization, role)

    def create_or_update_user(
        self,
        username: str,
        fullname: str,
        email: str,
        organization: str,
        role: str
    ):
        """Create or update a user."""
        if self.username == username:
            raise ValueError(f"Trying to create or update user with same name as service account! {self.username} {username}")

        try:
            user = self.get_user(username=username)
        except DatabaseUserDoesNotExistError:
            logging.info(f"Creating user {username=}")
            db_create_user(self.client, username, fullname, email, organization, role)
            return

        # Compare relevant attributes from the existing user and update if anything differs.
        existing_attrs = user.get("attributes", {})
        needs_update = any([
            fullname != existing_attrs.get("guac-full-name"),
            email != existing_attrs.get("guac-email-address"),
            organization != existing_attrs.get("guac-organization"),
            role != existing_attrs.get("guac-role")
        ])

        if needs_update:
            logging.info(f"Updating user {username=} (create_or_update)")
            db_update_user(self.client, username, fullname, email, organization, role)

    def delete_user(self, username: str):
        """Delete a user."""
        if self.username == username:
            raise ValueError(f"Trying to delete user with same name as service account! {self.username} {username}")

        logging.info(f"Delete user {username=}")
        db_delete_user(self.client, username)

    def list_connections(self):
        """List all connections."""
        return db_list_connections(self.client)

    def get_connection_id(self, conn_name: str):
        """Get connection ID by name."""
        conn_id = db_get_connection_by_name(self.client, conn_name)
        if conn_id is None:
            connections = self.list_connections()
            raise DatabaseConnectionDoesNotExistError(f"Connection does not exist! {conn_name} {connections}")
        return conn_id

    def get_connection(self, conn_id: int):
        """Get a connection by ID."""
        connection = db_get_connection(self.client, conn_id)
        if not connection:
            raise DatabaseConnectionDoesNotExistError(f"Connection {conn_id} does not exist")
        return connection

    def create_connection(
        self,
        name: str,
        protocol: str,
        parent: str,
        hostname: str,
        port: int
    ):
        """Create a new connection."""
        logging.info(f"Creating connection {name=}")
        return db_create_connection(
            self.client, name, protocol, parent, hostname, port
        )

    def update_connection(
        self,
        conn_id: int,
        name: str,
        protocol: str,
        parent: str,
        hostname: str,
        port: int
    ):
        """Update an existing connection."""
        logging.info(f"Updating connection {name=} {conn_id=}")
        db_update_connection(
            self.client, conn_id, name, protocol, parent, hostname, port
        )

    def create_or_update_connection(
        self,
        name: str,
        protocol: str,
        parent: str,
        hostname: str,
        port: int
    ):
        """Create or update a connection."""
        try:
            conn_id = self.get_connection_id(conn_name=name)

            # For now, always update if exists (like the original API code)
            needs_update = True

            if needs_update:
                self.update_connection(
                    conn_id=conn_id,
                    name=name,
                    protocol=protocol,
                    parent=parent,
                    hostname=hostname,
                    port=port
                )
                return conn_id

        except DatabaseConnectionDoesNotExistError:
            return self.create_connection(
                name=name,
                protocol=protocol,
                parent=parent,
                hostname=hostname,
                port=port
            )

    def delete_connection(self, conn_id: int):
        """Delete a connection."""
        logging.info(f"Delete connection {conn_id=}")
        db_delete_connection(self.client, conn_id)

    def create_user_connection(
        self,
        username: str,
        conn_id: int,
    ):
        """Grant a user permission to a connection."""
        logging.info(f"Create user connection {username=} {conn_id=}")
        db_create_user_connection(self.client, username, conn_id)

    def delete_user_connection(
        self,
        username: str,
        conn_id: int,
    ):
        """Revoke a user's permission to a connection."""
        logging.info(f"Delete user connection {username=} {conn_id=}")
        db_delete_user_connection(self.client, username, conn_id)

    def list_connection_users(self, conn_id: int):
        """List users with permission to a connection."""
        return db_list_connection_users(self.client, conn_id)
