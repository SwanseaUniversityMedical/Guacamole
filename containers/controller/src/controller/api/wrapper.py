import logging

from .authenticate_user import api_authenticate_user
from .error import APIUserDoesNotExistError
from .get_user import api_get_user
from .create_user import api_create_user
from .update_user import api_update_user


class API:

    hostname: str
    port: int
    username: str
    password: str
    data_source: str
    token: str

    def __init__(self,
        hostname: str,
        port: int,
        username: str,
        password: str,
        data_source: str,
    ):

        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.data_source = data_source

        self.token = api_authenticate_user(
            hostname=hostname,
            port=port,
            username=username,
            password=password
        )

    def create_or_update_user(self,
        username: str,
        fullname: str,
        email: str,
        organization: str,
        role: str
    ):

        try:
            user = api_get_user(
                hostname=self.hostname,
                port=self.port,
                token=self.token,
                data_source=self.data_source,
                username=username
            )

            needs_update = any([
                (fullname != user["attributes"]["guac-full-name"]),
                (email != user["attributes"]["guac-email-address"]),
                (organization != user["attributes"]["guac-organization"]),
                (role != user["attributes"]["guac-organizational-role"])
            ])

            if needs_update:
                logging.info(f"Updating user {username=}")
                return api_update_user(
                    hostname=self.hostname,
                    port=self.port,
                    token=self.token,
                    data_source=self.data_source,
                    username=username,
                    fullname=fullname,
                    email=email,
                    organization=organization,
                    role=role
                )

            else:
                logging.info(f"Skipping updating user {username=}")

        except APIUserDoesNotExistError:

            logging.info(f"Creating user {username=}")
            return api_create_user(
                hostname=self.hostname,
                port=self.port,
                token=self.token,
                data_source=self.data_source,
                username=username,
                fullname=fullname,
                email=email,
                organization=organization,
                role=role
            )
