"""
train new simple CNN model on MNIST
"""

import os
import requests

import torch
from torch import nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor
from dotenv import load_dotenv

from mlweb3.model import SimpleCNN


def main():
    load_dotenv()

    # data loaders
    data_train = DataLoader(
        datasets.MNIST('./etc/mnist', train=True, download=True, transform=ToTensor()),
        batch_size=64
    )
    data_test = DataLoader(
        datasets.MNIST('./etc/mnist', train=False, download=True, transform=ToTensor()),
        batch_size=64
    )

    # model
    model = SimpleCNN()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f'Using {device} device')
    model = model.to(device)
    print(model)

    # optimization
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adadelta(model.parameters(), lr=1.0)

    for i in range(10):
        print(f'Epoch: {i}')

        # train
        model.train()
        size = len(data_train.dataset)
        for batch, (X, y) in enumerate(data_train):
            X, y = X.to(device), y.to(device)

            # forward loss
            pred = model(X)
            loss = loss_fn(pred, y)

            # backpropagation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if batch % 100 == 0:
                loss, current = loss.item(), batch * len(X)
                print(f'  loss: {loss:>7f}  [{current:>5d}/{size:>5d}]')

        # test
        model.eval()
        size = len(data_test.dataset)
        num_batches = len(data_test)
        test_loss, correct = 0, 0
        with torch.no_grad():
            for X, y in data_test:
                X, y = X.to(device), y.to(device)
                pred = model(X)
                test_loss += loss_fn(pred, y).item()
                correct += (pred.argmax(1) == y).sum().item()

        print(f'test:\n  accuracy: {correct / size:>0.4f}\n  loss: {test_loss / num_batches:>8f}\n')

    # save
    os.makedirs('./etc/models', exist_ok=True)
    torch.save(model.state_dict(), './etc/models/cnn_mnist.pth')

    # upload to ipfs
    ipfs_auth = (os.getenv('INFURA_IPFS_ID'), os.getenv('INFURA_IPFS_KEY'))
    with open('./etc/models/cnn_mnist.pth', 'rb') as f:
        res = requests.post(
            'https://ipfs.infura.io:5001/api/v0/add',
            files={'cnn_mnist.pth': f},
            auth=ipfs_auth
        )
        res = res.json()
        print(f'{res["Name"]} uploaded to IPFS with hash: {res["Hash"]} and size: {res["Size"]}')

    mnist_files = {}
    for f in ['t10k-images-idx3-ubyte', 't10k-labels-idx1-ubyte', 'train-images-idx3-ubyte', 'train-labels-idx1-ubyte']:
        p = f'MNIST/raw/{f}'
        mnist_files[p] = open(f'./etc/mnist/{p}', 'rb')
    res = requests.post(
        'https://ipfs.infura.io:5001/api/v0/add',
        files=mnist_files,
        auth=ipfs_auth,
        params={'wrap-with-directory': True}
    )
    print('uploaded MNIST to IPFS:')
    print(res.text)

    for f in mnist_files.values():
        f.close()


if __name__ == '__main__':
    main()
