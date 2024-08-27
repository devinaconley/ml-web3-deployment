"""
inference logic for bacalhau job
"""

# lib
import os
import torch
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor, Compose

# src
from mlweb3.model import SimpleCNN


def main():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f'using device {device}')

    # load model
    print(f'loading SimpleCNN...')
    model = SimpleCNN()
    model.load_state_dict(torch.load('./etc/models/cnn_mnist.pth', map_location=torch.device(device)))
    model.eval()
    model = model.to(device)

    # get data
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
            X, y = X.to(device), y.to(device)
            pred = model(X)
            correct += (pred.argmax(1) == y).sum().item()
            total += len(X)
            predictions.extend(pred.argmax(1).cpu().numpy().tolist())

    print(f'test:\n  correct: {correct}\n  total: {total}\n  accuracy: {correct / total:>0.4f}')


if __name__ == '__main__':
    main()
