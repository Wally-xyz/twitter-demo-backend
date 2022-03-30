import json
import os
import rlp

from solcx import compile_source, install_solc
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from web3 import Web3
from web3.middleware import geth_poa_middleware

from app.src.config.parameter_store import Properties
from app.src.models.models import ABI
from eth_utils import to_bytes

from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig
from app.src.models.typedefs.EthereumNetwork import EthereumNetwork
from app.src.services.auth_service import get_current_user_id
from app.src.services.user_service import UserService

router = APIRouter(prefix="/contracts")
logger = LoggerConfig(__name__).get()


@router.get("/network")
def get_network():
    return {'network': Properties.network.name}


@router.post("/deploy", include_in_schema=(Properties.network != EthereumNetwork.MAINNET))
def deploy_base_contract(
        full_name: str = "Wally",
        short_name: str = "WALLY",
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id),
):
    user = UserService.get(db, user_id)
    if not user.admin and Properties.network == EthereumNetwork.MAINNET:
        raise Exception("Unauthorized to deploy contract to mainnet")
    logger.warning(f"User: {user.id} deploying contract name: {full_name}")
    class_name = "".join(full_name.split())
    contract = ("""
    //Contract based on https://docs.openzeppelin.com/contracts/3.x/erc721
    // SPDX-License-Identifier: MIT
    pragma solidity ^0.7.3;

    import "openzeppelin/token/ERC721/ERC721.sol";
    import "openzeppelin/utils/Counters.sol";
    import "openzeppelin/access/Ownable.sol";


    contract %(class_name)s is ERC721, Ownable {
        using Counters for Counters.Counter;
        Counters.Counter private _tokenIds;

        constructor() public ERC721("%(full_name)s", "%(short_name)s") {}

        function contractURI()
            public view 
            returns (string memory)
        {
            return "https://www.wallylabs.xyz/demo-contract-metadata.json";
        }

        function mintNFT(address recipient, string memory tokenURI)
            public onlyOwner
            returns (uint256)
        {
            _tokenIds.increment();

            uint256 newItemId = _tokenIds.current();
            _mint(recipient, newItemId);
            _setTokenURI(newItemId, tokenURI);

            return newItemId;
        }
    }
    """ % {"full_name": full_name, "short_name": short_name, "class_name": class_name}).strip()

    install_solc("0.7.3")
    compiled_sol = compile_source(contract)
    contract_interface = compiled_sol[f"<stdin>:{full_name}"]
    bytecode = contract_interface['bin']
    abi = contract_interface['abi']
    w3 = Web3(Web3.HTTPProvider(Properties.alchemy_node_url))
    if Properties.network == EthereumNetwork.RINKEBY:
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    minter = w3.eth.contract(abi=abi, bytecode=bytecode)
    gas = int(minter.constructor().estimateGas() * 1.5)
    nonce = w3.eth.getTransactionCount(Properties.vault_public_key)
    built_txn = minter.constructor().buildTransaction({
        'nonce': nonce,
        'gas': gas,
    })
    signed_txn = w3.eth.account.signTransaction(built_txn, private_key=Properties.vault_private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    # https://ethereum.stackexchange.com/questions/760/how-is-the-address-of-an-ethereum-contract-computed
    # answer by Mikko Ohtamaa
    # e.g. return sha3(rlp.encode([normalize_address(sender), nonce]))[12:]
    # normalize_address as bytes, nonce as int
    # take substring of hash output bytes and convert to hex string
    sender_bytes = to_bytes(hexstr=Properties.vault_public_key)
    raw = rlp.encode([sender_bytes, nonce])
    h = w3.keccak(raw)
    address_bytes = h[12:]
    contract_address = Web3.toChecksumAddress(address_bytes)

    abi_entry = ABI(
        contract_id=tx_hash.hex(),
        data=json.dumps(abi),
        address=contract_address
    )
    db.add(abi_entry)
    db.commit()
    return {
        'url': 'http://localhost:8000/mint?contract_id=%(contract_id)s' % {"contract_id": tx_hash.hex()},
        'gas': gas,
    }
