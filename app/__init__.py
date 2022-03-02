# from flask import Flask, request, jsonify
# import solcx
# from web3 import Web3
# import os
# from app.models import *
# import json
# from sendgrid.helpers.mail import Mail
# from sendgrid import SendGridAPIClient
#
# app = Flask(__name__)
#
# SQLALCHEMY_DATABASE_URI = (os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
#   if not os.environ.get('FLASK_ENV') == 'development'
#   else os.environ.get('DATABASE_URL'))
# app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#
# db.init_app(app)
#
# @app.route("/")
# def home():
#     return "<div>hello</div>"
#
# @app.route("/db")
# def db_create():
#   db.create_all()
#   return "<h1>Welcome to EasyMint</h1>"
#
# @app.route("/deploy")
# def hello_world():
#     full_name = request.args.get('full_name') if request.args.get('full_name') else "Reddit Year in Review"
#     class_name = "".join(full_name.split())
#     short_name = request.args.get('short_name') if request.args.get('short_name') else "RYIR"
#     contract = ("""
#     //Contract based on https://docs.openzeppelin.com/contracts/3.x/erc721
#     // SPDX-License-Identifier: MIT
#     pragma solidity ^0.7.3;
#
#     import "openzeppelin/token/ERC721/ERC721.sol";
#     import "openzeppelin/utils/Counters.sol";
#     import "openzeppelin/access/Ownable.sol";
#
#
#     contract %(class_name)s is ERC721, Ownable {
#         using Counters for Counters.Counter;
#         Counters.Counter private _tokenIds;
#
#         constructor() public ERC721("%(full_name)s", "%(short_name)s") {}
#
#         function mintNFT(address recipient, string memory tokenURI)
#             public onlyOwner
#             returns (uint256)
#         {
#             _tokenIds.increment();
#
#             uint256 newItemId = _tokenIds.current();
#             _mint(recipient, newItemId);
#             _setTokenURI(newItemId, tokenURI);
#
#             return newItemId;
#         }
#     }
#     """ % { "full_name": full_name, "short_name": short_name, "class_name": class_name }).strip()
#     compiled_sol = solcx.compile_source(contract)
#     contract_interface = compiled_sol["<stdin>:RedditYearinReview"]
#     bytecode = contract_interface['bin']
#     abi = contract_interface['abi']
#     w3 = Web3(Web3.HTTPProvider("https://eth-ropsten.alchemyapi.io/v2/i9WqOfyE1v7xbnr4_rdSld7Z6UJecfUB"))
#     Minter = w3.eth.contract(abi=abi, bytecode=bytecode)
#     built_txn = Minter.constructor().buildTransaction({
#         'nonce': w3.eth.getTransactionCount(w3.eth.account.from_key(os.environ.get("PRIVATE_KEY")).address),
#         'gas': 7000000,
#         'maxFeePerGas': w3.toWei('3', 'gwei'),
#         'maxPriorityFeePerGas': w3.toWei('3', 'gwei'),
#     })
#     signed_txn = w3.eth.account.signTransaction(built_txn, private_key=os.environ.get("PRIVATE_KEY"))
#     tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
#     txn_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
#     contract_address = txn_receipt.contractAddress
#     abi_entry = ABI(
#         contract_id=tx_hash.hex(),
#         data=json.dumps(abi),
#         address=contract_address
#     )
#     db.session.add(abi_entry)
#     db.session.commit()
#     return 'http://localhost:8000/mint?contract_id=%(contract_id)s' % { "contract_id": tx_hash.hex() }
#
# @app.route("/mint")
# def mint():
#     contract_id = request.args.get('contract_id')
#     username = request.args.get('username')
#     user = User.query.filter_by(username=username).first()
#     w3 = Web3(Web3.HTTPProvider("https://eth-ropsten.alchemyapi.io/v2/i9WqOfyE1v7xbnr4_rdSld7Z6UJecfUB"))
#     if not user:
#         account = w3.eth.account.create()
#         user = User(
#             private_key=account.privateKey,
#             username=username,
#             address=account.address
#         )
#         db.session.add(user)
#         db.session.commit()
#     address = user.address
#     contract = ABI.query.filter_by(contract_id=contract_id).first_or_404()
#     abi = contract.data
#     Minter = w3.eth.contract(abi=abi, address=contract.address)
#     built_txn = Minter.functions.mintNFT(address, "0x00").buildTransaction({
#         'nonce': w3.eth.getTransactionCount(w3.eth.account.from_key(os.environ.get("PRIVATE_KEY")).address),
#         'gas': 7000000,
#         'maxFeePerGas': w3.toWei('3', 'gwei'),
#         'maxPriorityFeePerGas': w3.toWei('3', 'gwei'),
#     })
#     signed_txn = w3.eth.account.signTransaction(built_txn, private_key=os.environ.get("PRIVATE_KEY"))
#     tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
#     return jsonify(tx_hash.hex())
#
# @app.route("/mint")
# def mint():
#     contract_id = request.args.get('contract_id')
#     email = request.args.get('email')
#     user = User.query.filter_by(email=email).first()
#     w3 = Web3(Web3.HTTPProvider("https://eth-ropsten.alchemyapi.io/v2/i9WqOfyE1v7xbnr4_rdSld7Z6UJecfUB"))
#     if not user:
#         account = w3.eth.account.create()
#         user = User(
#             private_key=account.privateKey,
#             username=email,
#             address=account.address,
#             email=email,
#         )
#         db.session.add(user)
#         db.session.commit()
#     address = user.address
#     contract = ABI.query.filter_by(contract_id=contract_id).first_or_404()
#     abi = contract.data
#     Minter = w3.eth.contract(abi=abi, address=contract.address)
#     built_txn = Minter.functions.mintNFT(address, "0x00").buildTransaction({
#         'nonce': w3.eth.getTransactionCount(w3.eth.account.from_key(os.environ.get("PRIVATE_KEY")).address),
#         'gas': 7000000,
#         'maxFeePerGas': w3.toWei('3', 'gwei'),
#         'maxPriorityFeePerGas': w3.toWei('3', 'gwei'),
#     })
#     signed_txn = w3.eth.account.signTransaction(built_txn, private_key=os.environ.get("PRIVATE_KEY"))
#     tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
#     token = generateRandomString()
#     maskedToken = sha1(token)
#     saveToken(user, maskedToken)
#     message = Mail(
#         from_email=('hello@zentacle.com', 'Zentacle'),
#         to_emails='mayank@zentacle.com')
#
#     message.template_id = 'd-df22c68e00c345108a3ac18ebf65bdaf'
#     message.dynamic_template_data = {
#         'org': 'Reddit',
#         'description': 'You were granted a NFT',
#         'url': 'http://localhost:8000/token?token='+token,
#     }
#     if not os.environ.get('FLASK_ENV') == 'development':
#       try:
#           sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
#           sg.send(message)
#       except Exception as e:
#           print(e.body)
#     return jsonify(tx_hash.hex())
#
# @app.route("/token")
# def retrieve():
#     token = request.args.get('token')
#     maskedToken = sha1(token)
#     user = User.query.filter_by(token=maskedToken)
#
#     user.
#
