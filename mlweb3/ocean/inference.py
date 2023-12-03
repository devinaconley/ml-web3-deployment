"""
inference logic for ocean model
"""
import os
import time
import datetime

from dotenv import load_dotenv

from brownie.network import accounts
from web3 import Web3
from ocean_lib.web3_internal.utils import connect_to_network
from ocean_lib.example_config import get_config_dict
from ocean_lib.ocean.ocean import Ocean
from ocean_lib.models.compute_input import ComputeInput


# TODO update to latest client version
def predict():
    # configure client
    load_dotenv()
    connect_to_network('mumbai')
    config = get_config_dict('mumbai')
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

    # resolve assets
    data_asset = ocean.assets.resolve('did:op:5e63539bd570ca76711dbe7e65fa2bebdfe694d840e7052519d58da6a1c848c1')
    weights_asset = ocean.assets.resolve('did:op:0533b845f2ece7ee7e7d9c2e299a2a383bc1085299fe24dbd5befef7e6e1e486')
    algo_asset = ocean.assets.resolve('did:op:335cdac9106166f690381e9056bb499007a00ea2100d21d2fc88b932bcaaad3a')

    data_token = ocean.get_datatoken(data_asset.datatokens[0]['address'])
    weights_token = ocean.get_datatoken(weights_asset.datatokens[0]['address'])
    algo_token = ocean.get_datatoken(algo_asset.datatokens[0]['address'])

    # mint tokens to user
    data_token.mint(bob_wallet.address, Web3.toWei(5, 'ether'), {'from': alice_wallet})
    weights_token.mint(bob_wallet.address, Web3.toWei(5, 'ether'), {'from': alice_wallet})
    algo_token.mint(bob_wallet.address, Web3.toWei(5, 'ether'), {'from': alice_wallet})

    # setup environment and inputs
    data_service = data_asset.services[0]
    weights_service = weights_asset.services[0]
    algo_service = algo_asset.services[0]
    free_c2d_env = ocean.compute.get_free_c2d_environment(data_service.service_endpoint)

    data_compute_input = ComputeInput(data_asset, data_service)
    weights_compute_input = ComputeInput(weights_asset, weights_service)
    algo_compute_input = ComputeInput(algo_asset, algo_service)

    # data_compute_input.transfer_tx_id = '0x8f9eb8f28402acf3d136edc063d2909059da2d418390eff52977f44548895197'
    # weights_compute_input.transfer_tx_id = '0x62c9b4ac3d0686d4354847f2f0be8a67b96b8e97a6582cfc675e12626279fc0d'
    # algo_compute_input.transfer_tx_id = '0x8b89f8dbcc0b2d9790c25cd403e264f9ccd876513f2926ae56ed1090fba26623'

    # pay for dataset, weights, and algo for 1 day
    datasets, algorithm = ocean.assets.pay_for_compute_service(
        datasets=[data_compute_input, weights_compute_input],
        algorithm_data=algo_compute_input,
        consume_market_order_fee_address=bob_wallet.address,
        wallet=bob_wallet,
        compute_environment=free_c2d_env['id'],
        valid_until=int((datetime.datetime.utcnow() + datetime.timedelta(days=1)).timestamp()),
        consumer_address=free_c2d_env['consumerAddress'],
    )
    assert datasets, 'payment for dataset unsuccessful'
    assert algorithm, 'payment for algorithm unsuccessful'

    # NOTE: not currently possible to use multiple input datasets on a single compute job

    # start compute job
    t0 = datetime.datetime.utcnow()
    job_id = ocean.compute.start(
        consumer_wallet=bob_wallet,
        dataset=datasets[0],
        compute_environment=free_c2d_env['id'],
        algorithm=algorithm,
        # additional_datasets=[datasets[1]]
    )
    print('Started compute job: {}'.format(job_id))

    # monitor job
    while 1:
        status = ocean.compute.status(data_asset, data_service, job_id, bob_wallet)
        t1 = datetime.datetime.utcnow()
        print('status: {}, time elapsed: {} seconds'.format(status['statusText'], t1 - t0))
        if status.get('dateFinished'):
            print(status)
            break
        time.sleep(10)

    # Retrieve algorithm output and log files
    output = ocean.compute.compute_job_result_logs(
        data_asset, data_service, job_id, bob_wallet
    )
    print(output)
