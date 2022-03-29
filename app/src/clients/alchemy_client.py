from collections import namedtuple
from dataclasses import dataclass

import requests

from app.src.config.logger_config import LoggerConfig
from app.src.config.parameter_store import Properties
from app.src.models.typedefs.EthereumNetwork import EthereumNetwork

BASE_URL = f"https://eth-mainnet.alchemyapi.io/v2/{Properties.alchemy_api_key}"
if Properties.network == EthereumNetwork.RINKEBY:
    BASE_URL = f"https://eth-rinkeby.alchemyapi.io/v2/{Properties.alchemy_api_key}"

GET_NFTS_URL = f"{BASE_URL}/getNFTs"

logger = LoggerConfig(__name__).get()


class AlchemyClient:

    @staticmethod
    def get_nfts(owner_address: str):
        resp = requests.get(url=GET_NFTS_URL,
                            params={"owner": owner_address})
        # nft = namedtuple("AlchemyNFTs", resp.json().keys())(*resp.json().values())
        # logger.info(f"Named tuple deserialize: {nft}")
        return resp.json()


# In some world I'd load the JSON into a more well-defined class. but not now
# class AlchemyAddress:
#     address: str
#
#
# class AlchemyID:
#     tokenId: str
#
#
# class AlchemyNFTs:
#     contract: AlchemyAddress
#     id: AlchemyID
