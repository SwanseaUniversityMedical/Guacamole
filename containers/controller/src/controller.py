import logging
import time

import kubernetes as k8s
import kopf
import click

from controller.database import (
    db_connection,
    db_create_service_user
)

from controller.api import API
from controller.directory import LDAP
from controller.sync import sync


# TODO Set logging level programmatically
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(funcName)s] %(message)s",
)


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
    "--guacamole-hostname",
    type=str,
    required=True,
    help="Url to the guacamole api.",
    show_default=True
)
@click.option(
    "--guacamole-port",
    type=int,
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
    guacamole_hostname: str,
    guacamole_port: int,
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
    logging.info(f"running {__file__}")

    logging.info("Connect to database")
    with db_connection(
        hostname=postgres_hostname,
        port=postgres_port,
        database=postgres_database,
        username=postgres_username,
        password=postgres_password
    ).begin() as database_client:

        logging.info("Create service user in database")
        db_create_service_user(
            client=database_client,
            username=guacamole_username,
            password=guacamole_password
        )

    logging.info("Authenticate with rest api as service user")
    api = API(
        hostname=guacamole_hostname,
        port=guacamole_port,
        username=guacamole_username,
        password=guacamole_password,
        data_source="postgresql"
    )

    logging.info("Authenticate with ldap as search bind")
    ldap = LDAP(
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

    logging.info("Load kube config")
    k8s.config.load_incluster_config()
    kopf.login_with_kubeconfig(k8s.config.load_incluster_config())

    @kopf.on.create('GuacamoleConnection')
    @kopf.on.update('GuacamoleConnection')
    @kopf.on.resume('GuacamoleConnection')
    @kopf.on.delete('GuacamoleConnection')
    def sync_on_event(spec):
        print("Syncing")
        # sync(
        #     kube_namespace=kube_namespace,
        #     ldap=ldap,
        #     api=api
        # )

    logging.info("Halting")


if __name__ == "__main__":
    main(auto_envvar_prefix='CONTROLLER')
