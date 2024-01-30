"""
flask app to run MNIST classifier as golem service
"""

# lib
import io
import base64

from flask import Flask, request
import torch
from torchvision.transforms import ToTensor, Compose
from PIL import Image

# src
from mlweb3.model import SimpleCNN

app = Flask(__name__)
model: SimpleCNN = None


@app.route('/')
def hello():
    return 'hello world', 200


@app.post('/classify')
def classify_image():
    body = request.json
    if 'image' not in body:
        return {}, 400
    image_data = body['image']

    # lazy load model
    global model
    if model is None:
        model = SimpleCNN()
        model.load_state_dict(torch.load('./etc/models/cnn_mnist.pth'))
        model.eval()

    # parse image data
    buffer = io.BytesIO(base64.b64decode(image_data))
    im = Image.open(buffer)

    # classification
    with torch.no_grad():
        # X, y = X.to(device), y.to(device)
        transform = Compose([ToTensor()])
        x = transform(im)
        x = x[None, :]  # add dimension for batch
        y = model(x)
    label = int(y.argmax(1))

    # respond
    print(f'received request from {request.user_agent}, image: {im.size}, predicted: {label}')

    return {'label': label, 'score': float(y[0, label])}, 200


def run():
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    run()
