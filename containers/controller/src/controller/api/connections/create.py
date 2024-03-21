# {
#   "parentIdentifier": "ROOT",
#   "name": "test",
#   "protocol": "rdp",
#   "parameters": {
#     "port": "",
#     "read-only": "",
#     "swap-red-blue": "",
#     "cursor": "",
#     "color-depth": "",
#     "clipboard-encoding": "",
#     "disable-copy": "",
#     "disable-paste": "",
#     "dest-port": "",
#     "recording-exclude-output": "",
#     "recording-exclude-mouse": "",
#     "recording-include-keys": "",
#     "create-recording-path": "",
#     "enable-sftp": "",
#     "sftp-port": "",
#     "sftp-server-alive-interval": "",
#     "enable-audio": "",
#     "security": "",
#     "disable-auth": "",
#     "ignore-cert": "",
#     "gateway-port": "",
#     "server-layout": "",
#     "timezone": "",
#     "console": "",
#     "width": "",
#     "height": "",
#     "dpi": "",
#     "resize-method": "",
#     "console-audio": "",
#     "disable-audio": "",
#     "enable-audio-input": "",
#     "enable-printing": "",
#     "enable-drive": "",
#     "create-drive-path": "",
#     "enable-wallpaper": "",
#     "enable-theming": "",
#     "enable-font-smoothing": "",
#     "enable-full-window-drag": "",
#     "enable-desktop-composition": "",
#     "enable-menu-animations": "",
#     "disable-bitmap-caching": "",
#     "disable-offscreen-caching": "",
#     "disable-glyph-caching": "",
#     "preconnection-id": "",
#     "hostname": "",
#     "username": "",
#     "password": "",
#     "domain": "",
#     "gateway-hostname": "",
#     "gateway-username": "",
#     "gateway-password": "",
#     "gateway-domain": "",
#     "initial-program": "",
#     "client-name": "",
#     "printer-name": "",
#     "drive-name": "",
#     "drive-path": "",
#     "static-channels": "",
#     "remote-app": "",
#     "remote-app-dir": "",
#     "remote-app-args": "",
#     "preconnection-blob": "",
#     "load-balance-info": "",
#     "recording-path": "",
#     "recording-name": "",
#     "sftp-hostname": "",
#     "sftp-host-key": "",
#     "sftp-username": "",
#     "sftp-password": "",
#     "sftp-private-key": "",
#     "sftp-passphrase": "",
#     "sftp-root-directory": "",
#     "sftp-directory": ""
#   },
#   "attributes": {
#     "max-connections": "",
#     "max-connections-per-user": "",
#     "weight": "",
#     "failover-only": "",
#     "guacd-port": "",
#     "guacd-encryption": "",
#     "guacd-hostname": ""
#   }
# }

import json
import logging
from urllib.parse import quote

import requests

from ..build_url import build_url


def api_create_connection(
    hostname: str,
    port: int,
    token: str,
    data_source: str,
    conn_name: str,
    conn_protocol: str,
    conn_parent: str,
    conn_hostname: str,
    conn_port: int
) -> dict:

    logging.debug(f"Creating connection {conn_name=}")
    response = requests.post(
        build_url(
            scheme="http",
            netloc=f"{hostname}:{port}",
            path=f"/api/session/data/{quote(data_source)}/connections",
            query=dict(
                token=token
            )
        ),
        data=json.dumps(dict(
            parentIdentifier=conn_parent,
            name=conn_name,
            protocol=conn_protocol,
            parameters={
                "hostname": conn_hostname,
                "port": str(conn_port)
            },
            attributes={

            }
        )),
        verify=False,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code not in (200,):
        ex = RuntimeError(("Bad status code!", response.status_code, response.text))
        logging.exception("Bad status code!", exc_info=ex)
        raise ex

    response = json.loads(response.text)
    logging.debug(f"{response=}")
    return response
