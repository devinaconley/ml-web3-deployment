"""
inference logic for bacalhau
"""

# lib
import time
from bacalhau_apiclient import Job, Task, InputSource, ResultPath, Resources, TimeoutConfig, SpecConfig, NetworkConfig
from bacalhau_apiclient.models.api_put_job_request import ApiPutJobRequest
from bacalhau_sdk.jobs import Jobs

IMAGE = 'devinaconley/mnist-pytorch-gpu:0.2'


def predict():
    # setup job
    task = Task(
        name='cnn_mnist_eval',
        engine=SpecConfig(
            type='docker',
            params=dict(Image=IMAGE)
        ),
        input_sources=[
            InputSource(
                alias='model',
                source=SpecConfig(type='ipfs', params=dict(CID='Qmduv29H6HeN1LBBR4WwQaaUNW7ZQuBCNWEPouXdMBhXS3')),
                target='/data/models/cnn_mnist.pth'
            ),
            InputSource(
                alias='data',
                source=SpecConfig(type='ipfs', params=dict(CID='QmYk9xig2e6twAuizfdRfgoJZFJZQiAQmh3VDKQY3YbYks')),
                target='/data/mnist/MNIST/raw'
            )
        ],
        result_paths=[ResultPath(
            name='output',
            path='/output'
        )],
        resources=Resources(
            cpu='0.25',
            memory='256mb',
            gpu='0'
        ),
        timeouts=TimeoutConfig(
            execution_timeout=300,
            queue_timeout=600
        ),
        publisher=SpecConfig(type='ipfs', params=dict()),

    )
    job = Job(
        name='mnist inference job',
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
    state = None
    while state != 'Completed':
        res = jobs.get(job_id)
        state = res.job.state.state_type
        if state in ['Pending', 'Queued', 'Running']:
            print(state)
            time.sleep(5)
            continue
        elif state == 'Failed':
            print(res.job.state.message)
            break

        print(state)
        print(res.job.tasks)
        print(f'job completed: {job_id}')

        res = jobs.results(job_id)
        print(f'results: {res}')
