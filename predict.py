"""
make predictions with deployed model on web3 infra
"""
import argparse

from mlweb3.ocean.inference import predict as predict_ocean
from mlweb3.fetch.inference import predict as predict_fetch


def main():
    args = parse_arguments()
    match args['infra']:
        case 'ocean':
            predict_ocean()
        case 'fetch':
            predict_fetch()


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infra', choices=['ocean', 'fetch'])
    return vars(parser.parse_args())


if __name__ == '__main__':
    main()
