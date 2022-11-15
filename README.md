# ml-web3-deployment
ML + web3 model deployment survey

## Setup

Create [miniconda](https://docs.conda.io/en/latest/miniconda.html) virtual environment
```
conda env create -f environment.yml
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

Deploy model to web3 infrastructure
```
python deploy --infra ocean
```
