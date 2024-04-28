# comment next line for testing
#FROM nvidia/cuda:12.1.1-runtime-ubuntu20.04
FROM python:3.10.13

WORKDIR /workspace

COPY image_builder.py app.py requirements.txt ./

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# by default out build function will add or replace entrypoint
# even if you set an entrypoint
