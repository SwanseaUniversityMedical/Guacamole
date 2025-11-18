import logging
import os
from typing import Dict, Any
import asyncio

import kubernetes as k8s
import kopf
import click

from controller.database import (
    db_connection,
    db_create_service_user,
    Database
)
from controller.directory import LDAP
from controller.sync import sync

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'DEBUG').upper(),
    format="[%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(funcName)s] %(message)s",
)

# Global configuration storage for kopf handlers
CONTROLLER_CONFIG = {}


def get_database_engine():
    """Get database engine using stored configuration."""
    config = CONTROLLER_CONFIG
    return db_connection(
        hostname=config['postgres_hostname'],
        port=config['postgres_port'],
        database=config['postgres_database'],
        username=config['postgres_username'],
        password=config['postgres_password']
    )


def get_ldap_client():
    """Get LDAP client using stored configuration."""
    config = CONTROLLER_CONFIG
    return LDAP(
        hostname=config['ldap_hostname'],
        port=config['ldap_port'],
        username=config['ldap_search_bind_dn'],
        password=config['ldap_search_bind_password'],
        user_base=config['ldap_user_base_dn'],
        user_filter=config['ldap_user_search_filter'],
        username_attribute=config['ldap_username_attribute'],
        fullname_attribute=config['ldap_fullname_attribute'],
        email_attribute=config['ldap_email_attribute'],
        group_base=config['ldap_group_base_dn'],
        group_filter=config['ldap_group_search_filter'],
        member_attribute=config['ldap_member_attribute'],
        paged_size=config['ldap_paged_size'],
    )


def perform_sync():
    """Perform synchronization using stored configuration."""
    try:
        with get_database_engine().connect() as database_client:
            database = Database(
                client=database_client,
                username=CONTROLLER_CONFIG['guacamole_username']
            )
            
            ldap = get_ldap_client()
            
            sync(
                kube_namespace=CONTROLLER_CONFIG['kube_namespace'],
                ldap=ldap,
                database=database
            )
    except Exception as e:
        logging.error(f"Sync failed: {e}")
        raise


# Kopf event handlers
@kopf.on.startup()
async def startup_handler(settings: kopf.OperatorSettings, **kwargs):
    """Handle operator startup."""
    logging.info("Guacamole Controller starting up...")
    
    # Configure kopf settings
    settings.posting.level = logging.INFO
    settings.watching.connect_timeout = 60
    settings.watching.server_timeout = 600
    
    logging.info("Startup completed successfully")


@kopf.on.cleanup()
async def cleanup_handler(**kwargs):
    """Handle operator cleanup."""
    logging.info("Guacamole Controller shutting down...")


@kopf.on.create('guacamole.ukserp.ac.uk', 'v1', 'guacamoleconnections', param="create")
@kopf.on.update('guacamole.ukserp.ac.uk', 'v1', 'guacamoleconnections', param="update")
@kopf.on.resume('guacamole.ukserp.ac.uk', 'v1', 'guacamoleconnections', param="resume")
async def handle_connection_event(body, name, namespace, param, **kwargs):
    """Handle GuacamoleConnection resource events."""
    logging.info(f"Handling {param} event for GuacamoleConnection {namespace}/{name}")
    
    try:
        # Perform sync operation
        await asyncio.get_event_loop().run_in_executor(None, perform_sync)
        
        logging.info(f"Successfully processed {param} for {namespace}/{name}")
        return {"message": f"GuacamoleConnection {name} processed successfully"}
        
    except Exception as e:
        logging.error(f"Failed to process {param} for {namespace}/{name}: {e}")
        raise kopf.TemporaryError(f"Sync failed: {e}", delay=60)


@kopf.on.delete('guacamole.ukserp.ac.uk', 'v1', 'guacamoleconnections')
async def handle_connection_deletion(body, name, namespace, **kwargs):
    """Handle GuacamoleConnection resource deletion."""
    logging.info(f"Handling deletion event for GuacamoleConnection {namespace}/{name}")
    
    try:
        # Perform sync operation (which will remove orphaned connections)
        await asyncio.get_event_loop().run_in_executor(None, perform_sync)
        
        logging.info(f"Successfully processed deletion for {namespace}/{name}")
        return {"message": f"GuacamoleConnection {name} deletion processed successfully"}
        
    except Exception as e:
        logging.error(f"Failed to process deletion for {namespace}/{name}: {e}")
        raise kopf.TemporaryError(f"Deletion sync failed: {e}", delay=60)


@kopf.timer('guacamole.ukserp.ac.uk', 'v1', 'guacamoleconnections', interval=300)
async def periodic_sync(body, name, namespace, **kwargs):
    """Perform periodic synchronization every 5 minutes."""
    logging.debug(f"Periodic sync for GuacamoleConnection {namespace}/{name}")
    
    try:
        await asyncio.get_event_loop().run_in_executor(None, perform_sync)
        logging.debug(f"Periodic sync completed for {namespace}/{name}")
        
    except Exception as e:
        logging.warning(f"Periodic sync failed for {namespace}/{name}: {e}")
        # Don't raise here as periodic sync failures shouldn't stop the operator


@click.command()
@click.option(
    "--postgres-hostname",
    type=str,
    required=True,
    help="Url to the postgres client.",
    show_default=True
)
@click.option(
    "--postgres-port",
    type=int,
    required=True,
    help="Port for the postgres client.",
    show_default=True
)
@click.option(
    "--postgres-database",
    type=str,
    required=True,
    help="Name of the postgres database.",
    show_default=True
)
@click.option(
    "--postgres-username",
    type=str,
    required=True,
    help="Auth username for the postgres client.",
    show_default=True
)
@click.option(
    "--postgres-password",
    type=str,
    required=True,
    help="Auth password for the postgres client.",
    show_default=True
)
@click.option(
    "--guacamole-username",
    type=str,
    required=True,
    help="Auth username for the guacamole controller account.",
    show_default=True
)
@click.option(
    "--guacamole-password",
    type=str,
    required=True,
    help="Auth password for the guacamole controller account.",
    show_default=True
)
@click.option(
    "--ldap-hostname",
    type=str,
    required=True,
    help="Url to the ldap server.",
    show_default=True
)
@click.option(
    "--ldap-port",
    type=int,
    required=True,
    help="Port for the ldap server.",
    show_default=True
)
@click.option(
    "--ldap-user-base-dn",
    type=str,
    required=True,
    help="LDAP base dn for valid users.",
    show_default=True
)
@click.option(
    "--ldap-group-base-dn",
    type=str,
    required=True,
    help="LDAP base dn for valid groups.",
    show_default=True
)
@click.option(
    "--ldap-username-attribute",
    type=str,
    required=True,
    help="LDAP username attribute of the user records.",
    show_default=True
)
@click.option(
    "--ldap-fullname-attribute",
    type=str,
    required=True,
    help="LDAP fullname attribute of the user records.",
    show_default=True
)
@click.option(
    "--ldap-email-attribute",
    type=str,
    required=True,
    help="LDAP email attribute of the user records.",
    show_default=True
)
@click.option(
    "--ldap-member-attribute",
    type=str,
    required=True,
    help="LDAP member attribute for querying membership.",
    show_default=True
)
@click.option(
    "--ldap-user-search-filter",
    type=str,
    required=True,
    help="LDAP search filter for user records.",
    show_default=True
)
@click.option(
    "--ldap-group-search-filter",
    type=str,
    required=True,
    help="LDAP search filter for group records.",
    show_default=True
)
@click.option(
    "--ldap-search-bind-dn",
    type=str,
    required=True,
    help="LDAP username for searching.",
    show_default=True
)
@click.option(
    "--ldap-search-bind-password",
    type=str,
    required=True,
    help="LDAP password for searching.",
    show_default=True
)
@click.option(
    "--ldap-paged-size",
    type=int,
    required=True,
    help="Number of results per page to request from the ldap server.",
    show_default=True
)
@click.option(
    "--kube-namespace",
    type=str,
    required=True,
    help="Namespace for looking for Guacamole CRD instances.",
    show_default=True
)
def main(
    postgres_hostname: str,
    postgres_port: int,
    postgres_database: str,
    postgres_username: str,
    postgres_password: str,
    guacamole_username: str,
    guacamole_password: str,
    ldap_hostname: str,
    ldap_port: int,
    ldap_user_base_dn: str,
    ldap_user_search_filter: str,
    ldap_username_attribute: str,
    ldap_fullname_attribute: str,
    ldap_email_attribute: str,
    ldap_group_base_dn: str,
    ldap_group_search_filter: str,
    ldap_member_attribute: str,
    ldap_search_bind_dn: str,
    ldap_search_bind_password: str,
    ldap_paged_size: int,
    kube_namespace: str
):
    """Main function that stores configuration and starts the kopf operator."""
    global CONTROLLER_CONFIG
    
    logging.info(f"running {__file__}")
    
    # Store configuration in global variable for kopf handlers
    CONTROLLER_CONFIG = {
        'postgres_hostname': postgres_hostname,
        'postgres_port': postgres_port,
        'postgres_database': postgres_database,
        'postgres_username': postgres_username,
        'postgres_password': postgres_password,
        'guacamole_username': guacamole_username,
        'guacamole_password': guacamole_password,
        'ldap_hostname': ldap_hostname,
        'ldap_port': ldap_port,
        'ldap_user_base_dn': ldap_user_base_dn,
        'ldap_user_search_filter': ldap_user_search_filter,
        'ldap_username_attribute': ldap_username_attribute,
        'ldap_fullname_attribute': ldap_fullname_attribute,
        'ldap_email_attribute': ldap_email_attribute,
        'ldap_group_base_dn': ldap_group_base_dn,
        'ldap_group_search_filter': ldap_group_search_filter,
        'ldap_member_attribute': ldap_member_attribute,
        'ldap_search_bind_dn': ldap_search_bind_dn,
        'ldap_search_bind_password': ldap_search_bind_password,
        'ldap_paged_size': ldap_paged_size,
        'kube_namespace': kube_namespace,
    }

    logging.info("Initialize database service user")
    database_engine = db_connection(
        hostname=postgres_hostname,
        port=postgres_port,
        database=postgres_database,
        username=postgres_username,
        password=postgres_password
    )
    
    with database_engine.begin() as database_client:
        db_create_service_user(
            client=database_client,
            username=guacamole_username,
            password=guacamole_password
        )

    logging.info("Test LDAP connection")
    try:
        ldap_test = LDAP(
            hostname=ldap_hostname,
            port=ldap_port,
            username=ldap_search_bind_dn,
            password=ldap_search_bind_password,
            user_base=ldap_user_base_dn,
            user_filter=ldap_user_search_filter,
            username_attribute=ldap_username_attribute,
            fullname_attribute=ldap_fullname_attribute,
            email_attribute=ldap_email_attribute,
            group_base=ldap_group_base_dn,
            group_filter=ldap_group_search_filter,
            member_attribute=ldap_member_attribute,
            paged_size=ldap_paged_size,
        )
        # Test the connection by accessing a simple attribute
        _ = ldap_test.hostname
        logging.info("LDAP connection test successful")
    except Exception as e:
        logging.warning(f"LDAP connection test failed: {e}")

    logging.info("Starting kopf operator...")
    # Run the kopf operator
    kopf.run()


if __name__ == "__main__":
    main(auto_envvar_prefix='CONTROLLER')
