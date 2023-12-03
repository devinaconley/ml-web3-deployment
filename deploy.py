"""
deploy trained model to web3 infra
"""
import argparse

from mlweb3.ocean.deployment import deploy as deploy_ocean
from mlweb3.fetch.deployment import deploy as deploy_fetch


def main():
    args = parse_arguments()
    match args['infra']:
        case 'ocean':
            deploy_ocean()
        case 'fetch':
            deploy_fetch()


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infra', choices=['ocean', 'fetch'])
    return vars(parser.parse_args())


if __name__ == '__main__':
    main()
