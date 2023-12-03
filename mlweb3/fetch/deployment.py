"""
deployment logic for fetch agent
"""
import os
import datetime

from dotenv import load_dotenv

from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low


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


@alice.on_interval(period=20.0)
async def health_check(ctx: Context):
    ctx.logger.info(f'health check: OK, service address: {alice.address}')


@alice.on_message(model=Request)
async def message_handler(ctx: Context, sender: str, msg: Request):
    ctx.logger.info(f'Received request from {sender[0:10]}, {msg.image}')
    response = Response(label=5, score=0.8)
    await ctx.send(sender, response)


def deploy():
    fund_agent_if_low(alice.wallet.address())
    alice.run()
