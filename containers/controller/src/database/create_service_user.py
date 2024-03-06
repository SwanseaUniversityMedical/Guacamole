import logging
import secrets
from hashlib import sha256

from sqlalchemy import text
from sqlalchemy.engine import Connection


def db_create_service_user(
    client: Connection,
    username: str,
    password: str
):

    logging.debug(f"{username=}")

    salt = secrets.token_hex(32).upper()
    logging.debug(f"{salt=}")

    password_hash = sha256(password.encode() + salt.encode()).hexdigest().upper()
    logging.debug(f"{password_hash=}")

    logging.info("creating user entity")
    client.execute(
        text(
            "INSERT INTO guacamole_entity (name, type) "
            "VALUES (:username, 'USER') "
            "ON CONFLICT DO NOTHING;"
        ),
        parameters=dict(
            username=username
        )
    )

    logging.info("creating user authentication")
    client.execute(
        text(
            "INSERT INTO guacamole_user (entity_id, password_hash, password_salt, password_date) "
            "SELECT "
            "   entity_id, "
            "   decode(:password, 'hex'), "
            "   decode(:salt, 'hex'), "
            "   CURRENT_TIMESTAMP "
            "FROM guacamole_entity WHERE name = :username AND guacamole_entity.type = 'USER' "
            "ON CONFLICT(entity_id) DO UPDATE SET "
            "   password_hash = excluded.password_hash, "
            "   password_salt = excluded.password_salt, "
            "   password_date = excluded.password_date;"
        ),
        parameters=dict(
            username=username,
            password=password_hash,
            salt=salt
        )
    )

    logging.info("assigning user permissions")
    client.execute(
        text(
            "INSERT INTO guacamole_system_permission (entity_id, permission) "
            "SELECT entity_id, permission::guacamole_system_permission_type "
            "FROM ( "
            "   VALUES "
            "       (:username, 'CREATE_CONNECTION'), "
            "       (:username, 'CREATE_CONNECTION_GROUP'), "
            "       (:username, 'CREATE_SHARING_PROFILE'), "
            "       (:username, 'CREATE_USER'), "
            "       (:username, 'CREATE_USER_GROUP'), "
            "       (:username, 'ADMINISTER') "
            ") permissions (username, permission) "
            "JOIN guacamole_entity ON "
            "   permissions.username = guacamole_entity.name AND guacamole_entity.type = 'USER' "
            "ON CONFLICT DO NOTHING;"
        ),
        parameters=dict(
            username=username
        )
    )
