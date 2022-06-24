from solcx import compile_standard   
from web3 import Web3
from decouple import config   
import json      
import os  
# open the file-> compile the file -> dump into json -> create contract in pyton -> create transection -> sign -> send.   // this is to deplooy contract .
# for update  -> create contract in python thorough abi and address-> create transection for the operation. -> sign -> send.

with open("./SimpleStorage.sol","r") as file:
    simple_storage_file = file.read()
     

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)
# will create as well as compiled_sol to file.
with open ("compiled_code.json","w") as file:
    json.dump(compiled_sol,file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = json.loads(
    compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["metadata"]
)["output"]["abi"]


# w3 = Web3(Web3.HTTPProvider(os.getenv("RINKEBY_RPC_URL")))
# chain_id = 4
#
# For connecting to ganache
w3 = Web3(Web3.HTTPProvider(config('Kovan_ABI')))
chain_id = 42
my_address = "0x95159B35aCd630712A179De5a83f9266ADDA7e3c"
private_key = config('PRIVATE_KEY')   # to use config import firtst and also download pip install python-decouple

# Create the contract in Python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address) 
balance = w3.eth.getBalance(my_address) 
print(nonce)
# Submit the transaction that deploys the contract
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gasPrice,
        "from": my_address,
        "nonce": nonce,
    }
)
# Sign the transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
print("Deploying Contract!")
# Send it!
tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
# Wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
print(f"Done! Contract deployed to {tx_receipt.contractAddress}")

#working with deployed contracts ..

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi = abi)
print (f"Initial stored value {simple_storage.functions.retrieve().call()}")
greeting_transection = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gasPrice,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
signed_getting_txn = w3.eth.account.sign_transaction(
    greeting_transection,private_key=private_key
)
tx_greeting_hash = w3.eth.sendRawTransaction(signed_getting_txn.rawTransaction)
print("updating stored value .... ")
tx_receipt = w3.eth.waitForTransactionReceipt(tx_greeting_hash)

print(simple_storage.functions.retrieve().call())



