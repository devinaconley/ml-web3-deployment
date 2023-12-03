"""
algorithm asset for ocean inference
"""

import os
import argparse
import json

import torch
from torch import nn
import torch.nn.functional as F

from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor


def main():
    args = parse_arguments()
    print(args)
    print(os.getcwd())

    if args['local']:
        filepath = args['weights']
    else:
        dids = os.getenv('DIDS', None)
        print(dids)
        if not dids:
            print('no DIDs found in environment. exiting.')
            return
        dids = json.loads(dids)
        if len(dids) == 0:
            print('no DID found for model. exiting.')
        filepath = f'data/inputs/{dids[0]}/0'

    # load model weights
    print(f'Loading SimpleCNN from {filepath}...')
    model = SimpleCNN()
    model.load_state_dict(torch.load(filepath))
    model.eval()

    # get/load data
    # TODO use local data when multiple input assets are supported
    os.makedirs('./etc/mnist', exist_ok=True)
    data = DataLoader(
        datasets.MNIST('./etc/mnist', train=False, download=True, transform=ToTensor()),
        batch_size=64
    )

    # do inference
    correct, total = 0, 0
    predictions = []
    with torch.no_grad():
        for X, y in data:
            # X, y = X.to(device), y.to(device)
            pred = model(X)
            correct += (pred.argmax(1) == y).sum().item()
            total += len(X)
            predictions.extend(pred.argmax(1).numpy().tolist())

    print(f'test:\n  accuracy: {correct / total:>0.4f}')

    # write output
    output_file = 'results.txt' if args['local'] else '/data/outputs/result'
    with open(output_file, 'w') as f:
        f.write(f'accuracy: {correct / total:>0.4f}\n\npredictions:\n')
        for p in predictions:
            f.write(f'{p}\n')


class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, (5, 5))
        self.conv2 = nn.Conv2d(32, 64, (5, 5))
        self.fc1 = nn.Linear(1024, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)
        x = F.softmax(x)
        return x


def parse_arguments() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--local', help='flag to indicate local development', action='store_true')
    parser.add_argument('-d', '--data', help='path to mnist input data')
    parser.add_argument('-w', '--weights', help='path to trained cnn model weights')

    return vars(parser.parse_args())


if __name__ == '__main__':
    main()
