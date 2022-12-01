"""
algorithm asset for ocean infernce
"""

import os
import argparse
import json


def main():
    args = parse_arguments()
    print(args)

    print(os.getcwd())

    dids = os.getenv('DIDS', None)
    print(dids)

    if not dids:
        print('No DIDs found in environment. Aborting.')
        return

    dids = json.loads(dids)
    for did in dids:
        filename = f'data/inputs/{did}/0'
        print(f'Reading asset file {filename}.')


def parse_arguments() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--local', help='flag to indicate local development', action='store_true')
    parser.add_argument('-d', '--data', help='path to mnist input data')
    parser.add_argument('-w', '--weights', help='path to trained cnn model weights')

    return vars(parser.parse_args())


if __name__ == '__main__':
    main()
