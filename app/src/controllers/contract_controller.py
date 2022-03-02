import json

import solcx
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from web3 import Web3
from web3.types import ABI

from app.src.config.database_config import get_db
from app.src.config.logger_config import LoggerConfig

router = APIRouter(prefix="/contracts")
logger = LoggerConfig(__name__).get()


@router.post("/deploy")
def deploy_base_contract(
        full_name: str = "Reddit Year in Review",
        short_name: str = "RYIR",
        db: Session = Depends(get_db)
):
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

    compiled_sol = solcx.compile_source(contract)
    contract_interface = compiled_sol["<stdin>:RedditYearinReview"]
    bytecode = contract_interface['bin']
    abi = contract_interface['abi']
    w3 = Web3(Web3.HTTPProvider("https://eth-ropsten.alchemyapi.io/v2/i9WqOfyE1v7xbnr4_rdSld7Z6UJecfUB"))
    Minter = w3.eth.contract(abi=abi, bytecode=bytecode)
    built_txn = Minter.constructor().buildTransaction({
        'nonce': w3.eth.getTransactionCount(w3.eth.account.from_key(os.environ.get("PRIVATE_KEY")).address),
        'gas': 7000000,
        'maxFeePerGas': w3.toWei('3', 'gwei'),
        'maxPriorityFeePerGas': w3.toWei('3', 'gwei'),
    })
    signed_txn = w3.eth.account.signTransaction(built_txn, private_key=os.environ.get("PRIVATE_KEY"))
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    txn_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = txn_receipt.contractAddress
    abi_entry = ABI(
        contract_id=tx_hash.hex(),
        data=json.dumps(abi),
        address=contract_address
    )
    db.add(abi_entry)
    db.commit()
    return f'http://localhost:8000/mint?contract_id={tx_hash.hex()}'
