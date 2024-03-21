import logging

from .error import APIConnectionDoesNotExistError, APIUserDoesNotExistError
from .authenticate_user import api_authenticate_user
from .connections.create import api_create_connection
from .connections.delete import api_delete_connection
from .connections.get import api_get_connection, api_get_connection_parameters
from .connections.list import api_list_connections
from .connections.update import api_update_connection
from .users.create_user_connection import api_create_user_connection
from .users.delete_user_connection import api_delete_user_connection
from .users.get import api_get_user, api_get_user_effective_permissions
from .users.create import api_create_user
from .users.delete import api_delete_user
from .users.list import api_list_users
from .users.update import api_update_user


class API:

    hostname: str
    port: int
    username: str
    password: str
    data_source: str
    token: str

    def __init__(
        self,
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

    def list_users(self):
        # logging.info(f"List users")
        return api_list_users(
            hostname=self.hostname,
            port=self.port,
            token=self.token,
            data_source=self.data_source
        )


    def get_user(self, username: str):
        # logging.info(f"Get user {username=}")
        return api_get_user(
            hostname=self.hostname,
            port=self.port,
            token=self.token,
            data_source=self.data_source,
            username=username
        )


    def get_user_effective_permissions(self, username: str):
        # logging.info(f"Get user effective permissions {username=}")
        return api_get_user_effective_permissions(
            hostname=self.hostname,
            port=self.port,
            token=self.token,
            data_source=self.data_source,
            username=username
        )

    def create_user(
        self,
        username: str,
        fullname: str,
        email: str,
        organization: str,
        role: str
    ):

        if self.username == username:
            raise ValueError(("Trying to create user with same name as service account!", self.username, username))

        logging.info(f"Creating user {username=}")
        api_create_user(
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


    def update_user(
        self,
        username: str,
        fullname: str,
        email: str,
        organization: str,
        role: str
    ):

        if self.username == username:
            raise ValueError(("Trying to update user with same name as service account!", self.username, username))

        logging.info(f"Updating user {username=}")
        api_update_user(
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

    def create_or_update_user(
        self,
        username: str,
        fullname: str,
        email: str,
        organization: str,
        role: str
    ):

        try:
            user = self.get_user(username=username)

            needs_update = any([
                (fullname != user["attributes"]["guac-full-name"]),
                (email != user["attributes"]["guac-email-address"]),
                (organization != user["attributes"]["guac-organization"]),
                (role != user["attributes"]["guac-organizational-role"])
            ])

            if needs_update:
                self.update_user(
                    username=username,
                    fullname=fullname,
                    email=email,
                    organization=organization,
                    role=role
                )

            # else:
            #     logging.info(f"Skipping updating user {username=}")

        except APIUserDoesNotExistError:

            self.create_user(
                username=username,
                fullname=fullname,
                email=email,
                organization=organization,
                role=role
            )

    def delete_user(self, username: str):

        if self.username == username:
            raise ValueError(("Trying to delete user with same name as service account!", self.username, username))

        logging.info(f"Delete user {username=}")
        api_delete_user(
            hostname=self.hostname,
            port=self.port,
            token=self.token,
            data_source=self.data_source,
            username=username
        )

    def list_connections(self):
        # logging.info(f"List connections")
        return api_list_connections(
            hostname=self.hostname,
            port=self.port,
            token=self.token,
            data_source=self.data_source
        )

    def get_connection_id(self, conn_name: str):

        connections = self.list_connections()

        for connection in connections.values():
            if connection["name"] == conn_name:
                return connection["identifier"]

        raise APIConnectionDoesNotExistError(("Connection does not exist!", conn_name, connections))

    def get_connection(self, conn_id: int):
        # logging.info(f"Get connection {conn_id=}")
        return api_get_connection(
            hostname=self.hostname,
            port=self.port,
            token=self.token,
            data_source=self.data_source,
            conn_id=conn_id
        )


    def get_connection_parameters(self, conn_id: int):
        # logging.info(f"Get connection parameters {conn_id=}")
        return api_get_connection_parameters(
            hostname=self.hostname,
            port=self.port,
            token=self.token,
            data_source=self.data_source,
            conn_id=conn_id
        )


    def create_connection(
        self,
        name: str,
        protocol: str,
        parent: str,
        hostname: str,
        port: int
    ):

        logging.info(f"Creating connection {name=}")
        response = api_create_connection(
            hostname=self.hostname,
            port=self.port,
            token=self.token,
            data_source=self.data_source,
            conn_name=name,
            conn_protocol=protocol,
            conn_parent=parent,
            conn_hostname=hostname,
            conn_port=port
        )

        return response["identifier"]


    def update_connection(
        self,
        conn_id: int,
        name: str,
        protocol: str,
        parent: str,
        hostname: str,
        port: int
    ):
        logging.info(f"Updating connection {name=} {conn_id=}")
        api_update_connection(
            hostname=self.hostname,
            port=self.port,
            token=self.token,
            data_source=self.data_source,
            conn_id=conn_id,
            conn_name=name,
            conn_protocol=protocol,
            conn_parent=parent,
            conn_hostname=hostname,
            conn_port=port
        )

    def create_or_update_connection(
        self,
        name: str,
        protocol: str,
        parent: str,
        hostname: str,
        port: int
    ):

        try:
            conn_id = self.get_connection_id(conn_name=name)

            connection = self.get_connection(conn_id=conn_id)
            connection_parameters = self.get_connection_parameters(conn_id=conn_id)

            # TODO determine if connection needs updating
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

            # else:
            #     logging.info(f"Skipping updating connection {name=}")


        except APIConnectionDoesNotExistError:

            return self.create_connection(
                name=name,
                protocol=protocol,
                parent=parent,
                hostname=hostname,
                port=port
            )

    def delete_connection(self, conn_id: int):
        logging.info(f"Delete connection {conn_id=}")
        api_delete_connection(
            hostname=self.hostname,
            port=self.port,
            token=self.token,
            data_source=self.data_source,
            conn_id=conn_id
        )

    def create_user_connection(
        self,
        username: str,
        conn_id: int,
    ):
        logging.info(f"Create user connection {username=} {conn_id=}")
        api_create_user_connection(
            hostname=self.hostname,
            port=self.port,
            token=self.token,
            data_source=self.data_source,
            username=username,
            conn_id=conn_id,
        )

    def delete_user_connection(
        self,
        username: str,
        conn_id: int,
    ):
        logging.info(f"Delete user connection {username=} {conn_id=}")
        api_delete_user_connection(
            hostname=self.hostname,
            port=self.port,
            token=self.token,
            data_source=self.data_source,
            username=username,
            conn_id=conn_id,
        )


    def list_connection_users(
        self,
        conn_id: int
    ):

        users = self.list_users()

        connection_users = dict()
        for user in users.values():

            username = user["username"]

            permissions = self.get_user_effective_permissions(username=username)

            if str(conn_id) not in permissions["connectionPermissions"]:
                continue

            if "READ" not in permissions["connectionPermissions"][str(conn_id)]:
                continue

            connection_users[username] = user

        return connection_users
