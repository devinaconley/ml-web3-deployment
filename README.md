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

Once the trained model has been uploaded to IPFS, define the `IPFS_MODEL_HASH` variable in your `.env` file

Deploy model to web3 infrastructure
```
python deploy.py --infra ocean
```

Make predictions with deployed model
```
python predict.py --infra ocean
```
