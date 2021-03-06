import os
from typing import Optional

import boto3

from app.src.models.typedefs.EthereumNetwork import EthereumNetwork

ssm_client = boto3.client("ssm")
env = os.environ.get("ENV", "dev")


def get_api_param(param: str, default: Optional[str] = None):
    try:
        return ssm_client.get_parameter(Name=f"/{env}/api/{param}")["Parameter"]["Value"]
    except Exception:
        if default:
            return default
        else:
            raise


class RelationalDB:
    @staticmethod
    def name(default=None):
        return get_api_param("db_name", default)

    @staticmethod
    def port(default=None):
        return get_api_param("db_port", default)

    @staticmethod
    def user(default=None):
        return get_api_param("db_username", default)

    @staticmethod
    def host(default=None):
        return get_api_param("db_host", default)

    @staticmethod
    def password(default=None):
        return get_api_param("db_password", default)


def determine_network(node_url: str) -> EthereumNetwork:
    for network in EthereumNetwork:
        if node_url.find(network.name.lower()) > 0:
            return network
    return EthereumNetwork.UNKNOWN


def determine_etherscan_url(network: EthereumNetwork) -> str:
    if network == EthereumNetwork.MAINNET:
        return "https://etherscan.io"
    elif network == EthereumNetwork.RINKEBY:
        return "https://rinkeby.etherscan.io"
    elif network == EthereumNetwork.ROBSTEN:
        return "https://ropsten.etherscan.io"
    else:
        return "https://etherscan.io"


def determine_opensea_url(network: EthereumNetwork) -> str:
    if network == EthereumNetwork.MAINNET:
        return "https://opensea.io"
    else:
        return "https://testnets.opensea.io"


class Properties:

    def __init__(self):
        self.sendgrid_api_key = get_api_param("sendgrid_api_key")
        self.pinata_jwt = get_api_param("pinata_jwt")
        self.authjwt_secret_key = get_api_param("authjwt_secret_key")
        self.base_domain = get_api_param("domain_url", "http://localhost")
        self.media_bucket = get_api_param("profile_pictures_bucket")
        self.stripe_api_key = get_api_param("stripe_api_key")
        self.frontend_url = get_api_param("frontend_url", "http://localhost:3000")
        self.vault_public_key = get_api_param("vault_public_key")
        self.vault_private_key = get_api_param("vault_private_key")
        self.alchemy_node_url = get_api_param("alchemy_node_url")
        self.alchemy_api_key = get_api_param("alchemy_api_key")
        self.alchemy_auth_token = get_api_param("alchemy_auth_token")
        self.kms_db_key_alias = get_api_param("kms_db_key_alias")
        # self.kms_vault_key = get_api_param("kms_db_key")
        self.stripe_price_id = get_api_param("stripe_price_id", "price_1KdEBBBRQJlh59702ERTzDWh")
        self.wally_api_key = get_api_param("wally_api_key")
        self.wally_api_url = get_api_param("wally_api_url", "http://localhost:8888")
        self.network = determine_network(self.alchemy_node_url)
        self.etherscan_url = determine_etherscan_url(self.network)
        self.opensea_url = determine_opensea_url(self.network)


# NOTE(john) - The purpose of these is to load the SSM params once on APP startup
# Otherwise each call to the parameter store is wasted time/latency
RelationalDB = RelationalDB()
Properties = Properties()
