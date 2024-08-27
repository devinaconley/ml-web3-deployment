# dockerfile for mnist classification job on bacalhau
FROM nvidia/cuda:11.3.1-cudnn8-runtime

# patch: https://github.com/NVIDIA/nvidia-container-toolkit/issues/258
RUN rm /etc/apt/sources.list.d/cuda.list
RUN rm /etc/apt/sources.list.d/nvidia-ml.list

# install python
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*
RUN python3 --version

# install packages
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cu113

# app
WORKDIR /mlweb3
COPY mlweb3/bacalhau/job.py job.py
COPY mlweb3/model.py mlweb3/model.py
COPY etc/models/cnn_mnist.pth etc/models/cnn_mnist.pth

CMD python3 job.py
