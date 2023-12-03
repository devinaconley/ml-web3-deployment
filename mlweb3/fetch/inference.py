"""
inference logic for fetch agent
"""

import io
import base64
import random

from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from torch.utils.data import Dataset
from torchvision import datasets


# note: redefining models because import seemed to break communications
class Request(Model):
    image: str


class Response(Model):
    label: int
    score: float


ALICE_ADDRESS = 'agent1qgy43mp9rl6mavzq7ga06d8nv2c54mrlw0z39kkw6dfavdhmyevn2vyzgt6'

bob = Agent(
    name='client',
    seed='mnist client seed',
    port=8001,
    endpoint=['http://127.0.0.1:8001/submit']
)

dataset: Dataset = None


@bob.on_interval(period=5.0)
async def classify_image(ctx: Context):
    # lazy load dataset
    global dataset
    if dataset is None:
        dataset = datasets.MNIST('./etc/mnist', train=False, download=True)  # , transform=ToTensor())

    # sample random image from test data
    idx = random.randrange(0, len(dataset))
    im, label = dataset[idx]

    # encode request
    with io.BytesIO() as buffer:
        im.save(buffer, format='png')
        data = base64.b64encode(buffer.getvalue())
    request = Request(image=data)

    ctx.logger.info(f'sending image classification request to {ALICE_ADDRESS[0:10]} (actual label: {label})')
    await ctx.send(ALICE_ADDRESS, request)


@bob.on_message(model=Response)
async def handle_response(ctx: Context, sender: str, msg: Response):
    ctx.logger.info(f'classification response from {sender[0:10]}, label: {msg.label}: score: {msg.score:.2f}')


def predict():
    fund_agent_if_low(bob.wallet.address())
    bob.run()
