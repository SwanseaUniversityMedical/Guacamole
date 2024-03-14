import asyncio
import logging
import typing

from .resource import Resource

class GuacamoleConnection(Resource):

    def __init__(
        self,
        name: str,
        manifest: dict,
        ldap_iter_group_members,
        ldap_username_attribute: str,
        api_token: str
    ):
        super().__init__(name=name, manifest=manifest)
        self.ldap_iter_group_members = ldap_iter_group_members
        self.ldap_username_attribute = ldap_username_attribute
        self.api_token = api_token

    def interval(self) -> int:
        return 30
        #return max(0, int(self.manifest["spec"]["interval"]))

    def sync(self):
        logging.info(f"Syncing {self}")
        try:

            # For now, just list off the members in the target group
            for record in self.ldap_iter_group_members(
                group_search_filter=self.manifest["spec"]["ldap"]["groupFilter"]
            ):
                dn = record["dn"]
                username = record["attributes"].get(self.ldap_username_attribute, "")
                logging.debug(f"Member {self} {dn=} {self.ldap_username_attribute}={username}")

        except Exception as ex:
            logging.exception("Sync error!", exc_info=ex)
            raise ex
