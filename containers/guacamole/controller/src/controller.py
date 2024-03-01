import logging
import click

from database import (
    db_connection,
    db_create_service_user
)

from api import (
    api_authenticate_user
)


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s %(filename)s:%(lineno)s %(funcName)s] %(message)s",
)


@click.command()
@click.option(
    "--postgres-hostname",
    type=str,
    required=True,
    help="Url to the postgres database.",
    show_default=True
)
@click.option(
    "--postgres-port",
    type=str,
    required=True,
    help="Port for the postgres database.",
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
    help="Auth username for the postgres database.",
    show_default=True
)
@click.option(
    "--postgres-password",
    type=str,
    required=True,
    help="Auth password for the postgres database.",
    show_default=True
)
@click.option(
    "--guacamole-hostname",
    type=str,
    required=True,
    help="Url to the guacamole api.",
    show_default=True
)
@click.option(
    "--guacamole-port",
    type=str,
    required=True,
    help="Port for the guacamole api.",
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
    type=str,
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
def main(
    postgres_hostname: str,
    postgres_port: str,
    postgres_database: str,
    postgres_username: str,
    postgres_password: str,
    guacamole_hostname: str,
    guacamole_port: str,
    guacamole_username: str,
    guacamole_password: str,
    ldap_hostname: str,
    ldap_port: str,
    ldap_user_base_dn: str,
    ldap_group_base_dn: str,
    ldap_username_attribute: str,
    ldap_member_attribute: str,
    ldap_user_search_filter: str,
    ldap_search_bind_dn: str,
    ldap_search_bind_password: str
):
    logging.info(f"running {__file__}")

    logging.info("connect to database")
    with db_connection(
        hostname=postgres_hostname,
        port=postgres_port,
        database=postgres_database,
        username=postgres_username,
        password=postgres_password
    ).begin() as database:

        logging.info("create service user in database")
        db_create_service_user(
            database=database,
            username=guacamole_username,
            password=guacamole_password
        )

    logging.info("authenticate with rest api as service user")
    token = api_authenticate_user(
        hostname=guacamole_hostname,
        port=guacamole_port,
        username=guacamole_username,
        password=guacamole_password
    )
    logging.debug(f"{token=}")

    logging.info("halting")


if __name__ == "__main__":
    main(auto_envvar_prefix='CONTROLLER')