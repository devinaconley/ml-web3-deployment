# ml-web3-deployment
ML + web3 model deployment survey

## Setup

Create primary [miniconda](https://docs.conda.io/en/latest/miniconda.html) virtual environment
```
conda env update -f environment.yml
```

Create virtual environments for specific web3 infra provider (e.g. for ocean)
```
conda env update -f etc/requirements/environment-ocean.yml
```

Activate virtual environment
```
conda activate mlweb3
```
or for specific provider
```
conda activate mlweb3[-provider]
```

Copy `.env.template` to `.env` and define variables

Update brownie configuration as needed for RPC access

For Golem support, also install the [yagna](https://docs.golem.network/docs/creators/python/examples/tools/yagna-installation-for-requestors) CLI and service


## Run

Train new model
```
python train.py
```

Once the trained model has been uploaded to IPFS, define the `IPFS_MODEL_HASH` variable in your `.env` file

Activate appropriate virtual environment (e.g. for ocean)
```
python activate mlweb3-ocean
```

Deploy model to web3 infrastructure
```
python deploy.py --infra ocean
```

Make predictions with deployed model
```
python predict.py --infra ocean
```
