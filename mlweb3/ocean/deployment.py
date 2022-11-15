"""
deployment logic for ocean model
"""
import os

from dotenv import load_dotenv

from brownie.network import accounts
from ocean_lib.web3_internal.utils import connect_to_network
from ocean_lib.example_config import ExampleConfig
from ocean_lib.ocean.ocean import Ocean


def setup():
    # configure client
    load_dotenv()
    connect_to_network('mumbai')
    config = ExampleConfig.get_config('mumbai')
    ocean = Ocean(config)
    print(config)

    # load accounts
    accounts.clear()
    alice_private_key = os.getenv('PRIVATE_KEY_0')
    alice_wallet = accounts.add(alice_private_key)
    alice_balance = accounts.at(alice_wallet.address).balance()
    print('Alice balance: {}'.format(alice_balance))
    assert alice_balance > 0

    bob_private_key = os.getenv('PRIVATE_KEY_1')
    bob_wallet = accounts.add(bob_private_key)
    bob_balance = accounts.at(bob_wallet.address).balance()
    print('Bob balance: {}'.format(bob_balance))
    assert bob_balance > 0
