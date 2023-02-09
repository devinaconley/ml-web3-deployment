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
from ocean_lib.example_config import ExampleConfig
from ocean_lib.ocean.ocean import Ocean
from ocean_lib.models.compute_input import ComputeInput


def predict():
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

    # resolve assets
    data_asset = ocean.assets.resolve('did:op:9a4c1fe5fcec7d4071b8afdbb17dcc2c05b1ecf8cf512f556ef8f38116a594c3')
    weights_asset = ocean.assets.resolve('did:op:733ca2bfe560f6a66cc1e5cc2b6b91799db77e5fdbd41d4e1a402cb944bcdf43')
    algo_asset = ocean.assets.resolve('did:op:0c3c2c9099c67a49128379e5781e48fccb6125d335464d07edcceae78e7f729c')

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
