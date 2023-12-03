# ml-web3-deployment
ML + web3 model deployment survey

## Setup

Create [miniconda](https://docs.conda.io/en/latest/miniconda.html) virtual environment

_Temp [workaround](https://github.com/yaml/pyyaml/issues/601#issuecomment-1813963845)_
```
conda create -n ml-web3-deployment python=3.10
conda activate ml-web3-deployment
pip install "cython<3.0.0" wheel
pip install "pyyaml==5.4.1" --no-build-isolation
```

_Install rest of environment_
```
conda env update -f environment.yml
```

Activate virtual environment
```
conda activate ml-web3-deployment
```

Copy `.env.template` to `.env` and define variables

Update brownie configuration as needed for RPC access


## Run

Train new model
```
python train.py
```

Once the trained model has been uploaded to IPFS, define the `IPFS_MODEL_HASH` variable in your `.env` file

Deploy model to web3 infrastructure
```
python deploy.py --infra ocean
```

Make predictions with deployed model
```
python predict.py --infra ocean
```
