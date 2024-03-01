import logging
import click

from tasks import (
    get_database_connection,
    create_user
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
    "--postgres-user",
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
    "--guacamole-controller-username",
    type=str,
    required=True,
    help="Auth username for the guacamole controller account.",
    show_default=True
)
@click.option(
    "--guacamole-controller-password",
    type=str,
    required=True,
    help="Auth password for the guacamole controller account.",
    show_default=True
)
def main(*args, **kwargs):
    logging.info(f"running {__file__}")

    with get_database_connection(**kwargs).begin() as database:

        create_user(
            database=database,
            username=kwargs["guacamole_controller_username"],
            password=kwargs["guacamole_controller_password"]
        )

    logging.info("halting")


if __name__ == "__main__":
    main(auto_envvar_prefix='INITDB')
