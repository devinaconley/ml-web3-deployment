"""
deployment logic for golem network
"""
# lib
import io
import base64
import asyncio
from typing import AsyncIterable

from dotenv import load_dotenv

import torch
from torchvision.transforms import ToTensor, Compose
from PIL import Image

from yapapi import Golem, Task, WorkContext
from yapapi.log import enable_default_logger
from yapapi.payload import vm

# src
from mlweb3.model import SimpleCNN

model: SimpleCNN = None


async def worker(context: WorkContext, tasks: AsyncIterable[Task]):
    async for task in tasks:
        script = context.new_script()
        future_result = script.run('/bin/sh', '-c', 'date')

        yield script

        task.accept_result(result=await future_result)


async def main():
    package = await vm.repo(image_hash='d646d7b93083d817846c2ae5c62c72ca0507782385a2e29291a3d376')
    tasks = [Task(data=None)]
    async with Golem(budget=1.0, subnet_tag='public') as golem:
        async for completed in golem.execute_tasks(worker, tasks, payload=package):
            print(completed.result.stdout)


def deploy():
    print('hello world')
    load_dotenv()
    loop = asyncio.get_event_loop()
    task = loop.create_task(main())
    loop.run_until_complete(task)
