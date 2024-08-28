"""
inference logic for bacalhau
"""

# lib
import time
import pprint
from bacalhau_apiclient.models.job import Job
from bacalhau_apiclient.models.task import Task
from bacalhau_apiclient.models.resources import Resources
from bacalhau_apiclient.models.timeout_config import TimeoutConfig
from bacalhau_apiclient.models.all_of_execution_published_result import SpecConfig
from bacalhau_apiclient.models.api_put_job_request import ApiPutJobRequest
from bacalhau_sdk.jobs import Jobs

IMAGE = 'devinaconley/mnist-pytorch-gpu:dev'


def predict():
    # setup job
    task = Task(
        name='My Main task',
        engine=SpecConfig(
            type='docker',
            params=dict(
                Image='ubuntu:latest',  # TODO
                Entrypoint=['/bin/bash'],
                Parameters=['-c', 'echo hello world'],
            ),
        ),
        resources=Resources(
            cpu='0.1',
            memory='256mb',
            gpu='0'
        ),
        timeouts=TimeoutConfig(
            execution_timeout=300,
            queue_timeout=600,
            total_timeout=1500
        ),
        publisher=SpecConfig(type='IPFS', params=dict()),

    )
    job = Job(
        name='a simple docker job',
        type='batch',
        count=1,
        tasks=[task]
    )
    job_req = ApiPutJobRequest(job=job)

    # submit
    jobs = Jobs()
    res = jobs.put(job_req)
    job_id = res.job_id
    print(res)

    # wait for completion
    while True:
        res = jobs.get(job_id)
        state = res.job.state.state_type
        if state in ['Pending', 'Queued']:
            print(state)
            time.sleep(5)
            continue
        elif state == 'Failed':
            print(res.job.state.message)
            break

        print(res.job)

        # TODO
        res0 = jobs.results(job_id)
        pprint.pprint(res0)

        res1 = jobs.history(job_id)
        pprint.pprint(res1)

        res2 = jobs.get(job_id)
        pprint.pprint(res2)

        res3 = jobs.executions(job_id)
        pprint.pprint(res3)
