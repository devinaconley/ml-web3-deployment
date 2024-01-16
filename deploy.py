"""
deploy trained model to web3 infra
"""
import argparse


def main():
    args = parse_arguments()
    match args['infra']:
        case 'ocean':
            from mlweb3.ocean.deployment import deploy
        case 'fetch':
            from mlweb3.fetch.deployment import deploy
            deploy()
        case 'golem':
            from mlweb3.golem.deployment import deploy
            deploy()
        case _:
            raise ValueError('unsupported infra')
    deploy()


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infra', choices=['ocean', 'fetch', 'golem'])
    return vars(parser.parse_args())


if __name__ == '__main__':
    main()
