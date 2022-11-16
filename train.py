"""
train new simple CNN model on MNIST
"""

import os

import torch
from torch import nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor

from mlweb3.model import SimpleCNN


def main():
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


if __name__ == '__main__':
    main()
