"""
deployment logic for ocean model
"""
import os
import datetime

from dotenv import load_dotenv

from brownie.network import accounts
from ocean_lib.web3_internal.utils import connect_to_network
from ocean_lib.example_config import ExampleConfig
from ocean_lib.ocean.ocean import Ocean
from ocean_lib.structures.file_objects import UrlFile, IpfsFile
from ocean_lib.services.service import Service


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

    # publish dataset
    data_nft = ocean.create_data_nft('MNIST dataset', 'MNIST', from_wallet=alice_wallet)
    print('Created data NFT: {}'.format(data_nft.address))

    data_token = data_nft.create_datatoken('MNIST dataset token', 'MNIST-DT', from_wallet=alice_wallet)
    print('Created data token: {}'.format(data_token.address))

    files = [
        UrlFile(url='https://ossci-datasets.s3.amazonaws.com/mnist/train-images-idx3-ubyte.gz'),
        UrlFile(url='https://ossci-datasets.s3.amazonaws.com/mnist/train-labels-idx1-ubyte.gz'),
        UrlFile(url='https://ossci-datasets.s3.amazonaws.com/mnist/t10k-images-idx3-ubyte.gz'),
        UrlFile(url='https://ossci-datasets.s3.amazonaws.com/mnist/t10k-labels-idx1-ubyte.gz')
    ]

    # create compute service
    compute_values = {
        'allowRawAlgorithm': False,
        'allowNetworkAccess': True,
        'publisherTrustedAlgorithms': [],
        'publisherTrustedAlgorithmPublishers': [],
    }
    compute_service = Service(
        service_id='2',
        service_type='compute',
        service_endpoint=ocean.config_dict['PROVIDER_URL'],
        datatoken=data_token.address,
        files=files,
        timeout=3600,
        compute_values=compute_values,
    )

    # publish asset with compute service on-chain
    created = '2022-11-16T12:00:00Z'  # str(datetime.datetime.utcnow())
    metadata = {
        'created': created,
        'updated': created,
        'description': 'MNIST handwritten digit database',
        'name': 'MNIST dataset',
        'type': 'dataset',
        'author': 'LeCun, Yann and Cortes, Corinna and Burges, CJ',
        'license': 'Unknown',
    }
    data_asset = ocean.assets.create(
        metadata=metadata,
        publisher_wallet=alice_wallet,
        files=files,
        services=[compute_service],
        data_nft_address=data_nft.address,
        deployed_datatokens=[data_token],
    )
    print('Published dataset asset DID: {}'.format(data_asset.did))

    # publish model weights
    weights_nft = ocean.create_data_nft('CNN MNIST weights', 'CNN-MNIST', from_wallet=alice_wallet)
    print('Created weights NFT: {}'.format(weights_nft.address))

    weights_token = weights_nft.create_datatoken('CNN MNIST weights token', 'CNN-MNIST-DT', from_wallet=alice_wallet)
    print('Created weights token: {}'.format(weights_token.address))

    files = [IpfsFile(hash=os.getenv('IPFS_MODEL_HASH'))]

    # create compute service
    compute_service = Service(
        service_id='2',
        service_type='compute',
        service_endpoint=ocean.config_dict['PROVIDER_URL'],
        datatoken=weights_token.address,
        files=files,
        timeout=3600,
        compute_values=compute_values,
    )

    # publish weights with compute service on-chain
    created = '2022-11-16T12:00:00Z'
    metadata = {
        'created': created,
        'updated': created,
        'description': 'CNN weights trained on MNIST handwritten digit database',
        'name': 'CNN MNIST weights',
        'type': 'dataset',
        'author': 'Alice',
        'license': 'Unknown',
    }
    weights_asset = ocean.assets.create(
        metadata=metadata,
        publisher_wallet=alice_wallet,
        files=files,
        services=[compute_service],
        data_nft_address=weights_nft.address,
        deployed_datatokens=[weights_token],
    )
    print('Published weights asset DID: {}'.format(weights_asset.did))
