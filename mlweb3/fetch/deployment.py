"""
deployment logic for fetch agent
"""
import io
import base64

import torch
from torchvision.transforms import ToTensor, Compose

from PIL import Image
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

from mlweb3.model import SimpleCNN


class Request(Model):
    image: str


class Response(Model):
    label: int
    score: float


alice = Agent(
    name='cnn-mnist',
    seed='cnn mnist agent seed',
    port=8000,
    endpoint=['http://127.0.0.1:8000/submit'],
)

model: SimpleCNN = None


@alice.on_interval(period=20.0)
async def health_check(ctx: Context):
    ctx.logger.info(f'health check: OK, service address: {alice.address}')


@alice.on_message(model=Request)
async def request_handler(ctx: Context, sender: str, msg: Request):
    # lazy load model
    global model
    if model is None:
        model = SimpleCNN()
        model.load_state_dict(torch.load('./etc/models/cnn_mnist.pth'))  # could also load from ipfs for remote hosting
        model.eval()

    # parse image data
    buffer = io.BytesIO(base64.b64decode(msg.image))
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
    ctx.logger.info(f'received request from {sender[0:10]}, image: {im.size}, predicted: {label}')
    response = Response(label=label, score=y[0, label])
    await ctx.send(sender, response)


def deploy():
    fund_agent_if_low(alice.wallet.address())
    alice.run()
