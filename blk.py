

import json
from web3 import Web3, HTTPProvider


# # If Ganache runs on 8545:
# web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# truffle development blockchain address
blockchain_address = 'http://127.0.0.1:8545'
# Client instance to interact with the blockchain
web3 = Web3(HTTPProvider(blockchain_address))
# Set the default account (so we don't need to set the "from" for every transaction call)
web3.eth.defaultAccount = web3.eth.accounts[0]
compiled_contract_path = 'D:/python/Blockeste/node_modules/.bin/build/contracts/LandRegistration.json'
# Deployed contract address (see `migrate` command output: `contract address`)
deployed_contract_address = '0xf3D138c8b53Feb20a2af3B58Dcc88648171bD69E'
syspath=r"D:\python\Blockeste\static\\"




