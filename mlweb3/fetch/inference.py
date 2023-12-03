"""
inference logic for fetch agent
"""

from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low


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


@bob.on_interval(period=5.0)
async def classify_image(ctx: Context):
    ctx.logger.info(f'Sending classification request to {ALICE_ADDRESS[0:10]}')
    request = Request(image="0xtestdata")
    await ctx.send(ALICE_ADDRESS, request)


@bob.on_message(model=Response)
async def handle_response(ctx: Context, sender: str, msg: Response):
    ctx.logger.info(f'Classification response from {sender[0:10]}, label: {msg.label}: score {msg.score}')


def predict():
    fund_agent_if_low(bob.wallet.address())
    bob.run()
