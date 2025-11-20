import logging
import os
from typing import Dict, Any
import asyncio

import kubernetes as k8s
import kopf

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

# Global configuration storage - populated from environment variables
CONTROLLER_CONFIG = {}


def get_env_int(key: str, default: int) -> int:
    """Safely get an integer environment variable with a default value."""
    value = os.getenv(key)
    if value is None or value.strip() == '':
        return default
    try:
        return int(value)
    except ValueError:
        logging.warning(f"Invalid integer value for {key}: '{value}', using default {default}")
        return default


def load_configuration_from_env():
    """Load configuration from environment variables."""
    config = {
        # Database configuration
        'postgres_hostname': os.getenv('CONTROLLER_POSTGRES_HOSTNAME'),
        'postgres_port': get_env_int('CONTROLLER_POSTGRES_PORT', 5432),
        'postgres_database': os.getenv('CONTROLLER_POSTGRES_DATABASE'),
        'postgres_username': os.getenv('CONTROLLER_POSTGRES_USERNAME'),
        'postgres_password': os.getenv('CONTROLLER_POSTGRES_PASSWORD'),
        'guacamole_username': os.getenv('CONTROLLER_GUACAMOLE_USERNAME'),
        'guacamole_password': os.getenv('CONTROLLER_GUACAMOLE_PASSWORD'),
        
        # LDAP configuration
        'ldap_hostname': os.getenv('CONTROLLER_LDAP_HOSTNAME'),
        'ldap_port': get_env_int('CONTROLLER_LDAP_PORT', 389),
        'ldap_user_base_dn': os.getenv('CONTROLLER_LDAP_USER_BASE_DN'),
        'ldap_user_search_filter': os.getenv('CONTROLLER_LDAP_USER_SEARCH_FILTER'),
        'ldap_username_attribute': os.getenv('CONTROLLER_LDAP_USERNAME_ATTRIBUTE'),
        'ldap_fullname_attribute': os.getenv('CONTROLLER_LDAP_FULLNAME_ATTRIBUTE'),
        'ldap_email_attribute': os.getenv('CONTROLLER_LDAP_EMAIL_ATTRIBUTE'),
        'ldap_group_base_dn': os.getenv('CONTROLLER_LDAP_GROUP_BASE_DN'),
        'ldap_group_search_filter': os.getenv('CONTROLLER_LDAP_GROUP_SEARCH_FILTER'),
        'ldap_member_attribute': os.getenv('CONTROLLER_LDAP_MEMBER_ATTRIBUTE'),
        'ldap_search_bind_dn': os.getenv('CONTROLLER_LDAP_SEARCH_BIND_DN'),
        'ldap_search_bind_password': os.getenv('CONTROLLER_LDAP_SEARCH_BIND_PASSWORD'),
        'ldap_paged_size': get_env_int('CONTROLLER_LDAP_PAGED_SIZE', 100),
        
        # Kubernetes configuration
        'kube_namespace': os.getenv('CONTROLLER_KUBE_NAMESPACE'),
    }
    
    # Validate required configuration
    required_keys = [
        'postgres_hostname', 'postgres_database', 'postgres_username', 'postgres_password',
        'guacamole_username', 'guacamole_password',
        'ldap_hostname', 'ldap_user_base_dn', 'ldap_user_search_filter',
        'ldap_username_attribute', 'ldap_fullname_attribute', 'ldap_email_attribute',
        'ldap_group_base_dn', 'ldap_group_search_filter', 'ldap_member_attribute',
        'ldap_search_bind_dn', 'ldap_search_bind_password', 'kube_namespace'
    ]
    
    missing_keys = [key for key in required_keys if not config.get(key)]
    if missing_keys:
        raise RuntimeError(f"Missing required environment variables: {missing_keys}")
    
    return config


def get_database_engine():
    """Get database engine using stored configuration."""
    config = CONTROLLER_CONFIG
    
    # Check if configuration is available
    required_keys = ['postgres_hostname', 'postgres_port', 'postgres_database', 
                     'postgres_username', 'postgres_password']
    
    for key in required_keys:
        if key not in config:
            raise RuntimeError(f"Controller configuration not initialized: missing {key}")
    
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
    
    # Check if configuration is available
    required_keys = ['ldap_hostname', 'ldap_port', 'ldap_search_bind_dn', 
                     'ldap_search_bind_password', 'ldap_user_base_dn',
                     'ldap_user_search_filter', 'ldap_username_attribute',
                     'ldap_fullname_attribute', 'ldap_email_attribute',
                     'ldap_group_base_dn', 'ldap_group_search_filter',
                     'ldap_member_attribute', 'ldap_paged_size']
    
    for key in required_keys:
        if key not in config:
            raise RuntimeError(f"Controller configuration not initialized: missing {key}")
    
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
    """Handle operator startup and initialization."""
    global CONTROLLER_CONFIG
    
    logging.info("Guacamole Controller starting up...")
    
    # Configure kopf settings
    settings.posting.level = logging.INFO
    settings.watching.connect_timeout = 60
    settings.watching.server_timeout = 600
    
    try:
        # Load configuration from environment variables
        logging.info("Loading configuration from environment variables...")
        CONTROLLER_CONFIG = load_configuration_from_env()
        logging.info("Configuration loaded successfully")
        
        # Initialize database service user
        logging.info("Initializing database service user...")
        database_engine = get_database_engine()
        with database_engine.begin() as database_client:
            db_create_service_user(
                client=database_client,
                username=CONTROLLER_CONFIG['guacamole_username'],
                password=CONTROLLER_CONFIG['guacamole_password']
            )
        logging.info("Database service user initialized")
        
        # Test LDAP connection
        logging.info("Testing LDAP connection...")
        try:
            ldap_test = get_ldap_client()
            # Test the connection by accessing a simple attribute
            _ = ldap_test.hostname
            logging.info("LDAP connection test successful")
        except Exception as e:
            logging.warning(f"LDAP connection test failed: {e}")
        
        logging.info("Startup completed successfully")
        
    except Exception as e:
        logging.error(f"Startup failed: {e}")
        raise


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
        # Perform sync operation (configuration is guaranteed to be available from startup)
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
        # Configuration is guaranteed to be available from startup
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


def main():
    """Main entry point - start the kopf operator."""
    logging.info(f"Starting Guacamole Controller from {__file__}")
    
    # Run the kopf operator (configuration loaded in startup handler)
    kopf.run()


if __name__ == "__main__":
    main()
