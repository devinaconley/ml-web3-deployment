"""
deployment logic for ocean model
"""
import os
import datetime

from dotenv import load_dotenv

from brownie.network import accounts
from ocean_lib.web3_internal.utils import connect_to_network
from ocean_lib.example_config import get_config_dict
from ocean_lib.ocean.ocean import Ocean
from ocean_lib.structures.file_objects import UrlFile, IpfsFile
from ocean_lib.services.service import Service


def deploy():
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

    # publish algorithm
    algo_nft = ocean.create_data_nft('CNN inference', 'CNN', from_wallet=alice_wallet)
    print('Created algorithm NFT: {}'.format(algo_nft.address))

    algo_token = algo_nft.create_datatoken('CNN inference token', 'CNN-DT', from_wallet=alice_wallet)
    print('Created algorithm token: {}'.format(algo_token.address))

    metadata = {
        'created': created,
        'updated': created,
        'description': 'Algorithm to perform CNN inference on the MNIST dataset',
        'name': 'CNN MNIST inference',
        'type': 'algorithm',
        'author': 'Alice',
        'license': 'Unknown',
        'algorithm': {
            'language': 'python',
            'format': 'docker-image',
            'version': '0.1',
            'container': {
                'entrypoint': 'python $ALGO',
                'image': 'pytorch/pytorch',
                'tag': '1.12.1-cuda11.3-cudnn8-runtime',
                'checksum': 'sha256:0bc0971dc8ae319af610d493aced87df46255c9508a8b9e9bc365f11a56e7b75',
            },
        }
    }

    # publish algorithm asset
    algo_asset = ocean.assets.create(
        metadata=metadata,
        publisher_wallet=alice_wallet,
        files=[UrlFile('https://gist.githubusercontent.com/devinaconley/c16f440d5aa3e647ee7555f32824a768/raw/ocean_mnist_inference.py')],
        data_nft_address=algo_nft.address,
        deployed_datatokens=[algo_token],
    )
    print('Published algorithm asset DID: {}'.format(algo_asset.did))

    # authorize algorithm on data and model assets
    compute_service = data_asset.services[0]
    compute_service.add_publisher_trusted_algorithm(algo_asset)
    data_asset = ocean.assets.update(data_asset, alice_wallet)
    print('Authorized dataset {} for use with algorithm {}'.format(data_asset.did, algo_asset.did))

    compute_service = weights_asset.services[0]
    compute_service.add_publisher_trusted_algorithm(algo_asset)
    weights_asset = ocean.assets.update(weights_asset, alice_wallet)
    print('Authorized weights {} for use with algorithm {}'.format(weights_asset.did, algo_asset.did))
