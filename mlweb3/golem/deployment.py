"""
deployment logic for golem network
"""
# lib
import asyncio
from typing import AsyncIterable
from datetime import timedelta, datetime
from dotenv import load_dotenv

from yapapi import Golem, Task, WorkContext
from yapapi.log import enable_default_logger
from yapapi.payload import vm

from yapapi import Golem
from yapapi.contrib.service.http_proxy import HttpProxyService, LocalHttpProxy
from yapapi.payload import vm
from yapapi.services import Service, ServiceState

# src
from mlweb3.golem.app import run

LOCAL = False  # set true for local flask app development
PORT = 5000
IMAGE_HASH = '8a1e55e6e7212cbc4754b74a6d590809d47708bada50fee9ecb15dd0'


class ClassifierService(HttpProxyService):
    def __init__(self):
        super().__init__(remote_port=PORT)

    @staticmethod
    async def get_payload():
        return await vm.repo(
            image_hash=IMAGE_HASH,
            capabilities=['vpn'],
        )

    async def start(self):
        async for script in super().start():
            yield script

        script = self._ctx.new_script(timeout=None)
        script.run("/bin/bash", "-c", 'python3 app.py > /mlweb3/out 2> /mlweb3/err &')
        yield script

    async def reset(self):
        pass


async def main():
    async with Golem(budget=1.0, subnet_tag='public') as golem:
        print(f'connecting to golem subnet: {golem.subnet_tag} and network: {golem.payment_network}')

        network = await golem.create_network('192.168.0.1/24')
        async with network:
            # deploy service
            print('starting classifier service...')
            cluster = await golem.run_service(ClassifierService, network=network)
            instance = cluster.instances[0]
            print(cluster)

            t0 = datetime.now()
            waiting = True
            while waiting:
                dt = datetime.now() - t0
                print(f'elapsed: {dt}, status: {instance.state}')
                if dt > timedelta(minutes=15):
                    raise Exception(f'timeout starting cluster instances {cluster}, after {dt}')
                waiting = any(i.state in (ServiceState.pending, ServiceState.starting) for i in cluster.instances)
                await asyncio.sleep(5)

            print(f'started classifier service on {cluster} after {dt}')

            # launch local proxy
            proxy = LocalHttpProxy(cluster, PORT)
            await proxy.run()

            print(f'local proxy listening on http://localhost:{PORT}')

            # run until interrupt
            while True:
                print(cluster.instances)
                try:
                    await asyncio.sleep(10)
                except (KeyboardInterrupt, asyncio.CancelledError):
                    break

            # shutdown
            print('stopping proxy...')
            await proxy.stop()

            print('stopping cluster...')
            cluster.stop()
            while any(s.is_available for s in cluster.instances):
                print(cluster.instances)
                await asyncio.sleep(5)

            print('done.')


def deploy():
    if LOCAL:
        run(port=PORT)
        return
    print('deploying to golem network...')
    load_dotenv()
    loop = asyncio.get_event_loop()
    task = loop.create_task(main())
    loop.run_until_complete(task)
