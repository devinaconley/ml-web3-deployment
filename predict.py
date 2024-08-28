"""
make predictions with deployed model on web3 infra
"""
import argparse


def main():
    args = parse_arguments()
    match args['infra']:
        case 'ocean':
            from mlweb3.ocean.inference import predict
        case 'fetch':
            from mlweb3.fetch.inference import predict
        case 'golem':
            from mlweb3.golem.inference import predict
        case 'bacalhau':
            from mlweb3.bacalhau.inference import predict
        case _:
            raise ValueError('unsupported infra')
    predict()


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infra', choices=['ocean', 'fetch', 'golem', 'bacalhau'])
    return vars(parser.parse_args())


if __name__ == '__main__':
    main()
