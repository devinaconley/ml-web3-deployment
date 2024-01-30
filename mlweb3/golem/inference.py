"""
inference logic for golem client
"""

import io
import base64
import random

import requests
from torch.utils.data import Dataset
from torchvision import datasets

SERVICE_HOST = 'http://127.0.0.1'
SERVICE_PORT = 5000

dataset: Dataset = None


def classify_image():
    # sample random image from test data
    idx = random.randrange(0, len(dataset))
    im, label = dataset[idx]

    # encode request
    with io.BytesIO() as buffer:
        im.save(buffer, format='png')
        data = base64.b64encode(buffer.getvalue())

    print(f'sending image classification request to service (actual label: {label})')
    res = requests.post(
        url=f'{SERVICE_HOST}:{SERVICE_PORT}/classify',
        json={'image': data.decode('utf-8')}
    )
    if res.status_code != 200:
        print(res.text)
        return
    body = res.json()
    print(f'classification response from service, label: {body["label"]}: score: {body["score"]:.2f}')


def predict():
    res = requests.get(url=f'{SERVICE_HOST}:{SERVICE_PORT}')
    print(res.text)

    global dataset
    dataset = datasets.MNIST('./etc/mnist', train=False, download=True)
    for _ in range(100):
        classify_image()
