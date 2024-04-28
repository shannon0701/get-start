import os
import time

import everai.utils.cmd
from everai.app import App, context, VolumeRequest
from everai.autoscaling import SimpleAutoScalingPolicy
from everai.image import Image, BasicAuth
from everai.resource_requests import ResourceRequests
from everai.placeholder import Placeholder
import flask
from image_builder import IMAGE

VOLUME_NAME = 'get-start-volume'
QUAY_IO_SECRET_NAME = 'quay-secret'
CONFIGMAP_NAME = 'get-start-configmap'
MODEL_FILE_NAME = 'my-model'

image = Image.from_registry(IMAGE, auth=BasicAuth(
        username=Placeholder(QUAY_IO_SECRET_NAME, 'username', kind='Secret'),
        password=Placeholder(QUAY_IO_SECRET_NAME, 'password', kind='Secret'),
    ))

app = App(
    'get-start',
    image=image,
    volume_requests=[
        VolumeRequest(name=VOLUME_NAME, create_if_not_exists=True),
    ],
    secret_requests=[QUAY_IO_SECRET_NAME],
    configmap_requests=[CONFIGMAP_NAME],
    resource_requests=ResourceRequests(
        cpu_num=1,
        memory_mb=1024,
    ),
    autoscaling_policy=SimpleAutoScalingPolicy(
        min_workers=Placeholder(kind='ConfigMap', name=CONFIGMAP_NAME, key='min_workers'),
        max_workers=Placeholder(kind='ConfigMap', name=CONFIGMAP_NAME, key='max_workers'),
        max_queue_size=Placeholder(kind='ConfigMap', name=CONFIGMAP_NAME, key='max_queue_size'),
        max_idle_time=Placeholder(kind='ConfigMap', name=CONFIGMAP_NAME, key='max_idle_time'),
        scale_up_step=Placeholder(kind='ConfigMap', name=CONFIGMAP_NAME, key='scale_up_step'),
    ),
)


# https://everai.expvent.com/api/v1/apps/get-start/txt2img
# curl -X POST -H'Content-Type: application/json' http://localhost:8866/txt2img/jone -d '{"prompt": "say hello to"}'
@app.service.route('/txt2img/<name>', methods=['POST'])
def txt2img(name: str):
    data = flask.request.json
    print(data)
    prompt = data['prompt']
    time.sleep(3)
    return f"{prompt} - {name}"


# curl http://localhost:8866/show-volume
@app.service.route('/show-volume', methods=['GET'])
def show_volume():
    volume = context.get_volume(VOLUME_NAME)
    model_path = os.path.join(volume.path, MODEL_FILE_NAME)
    with open(model_path, 'r') as f:
        return f.read()


# https://everai.expvent.com/api/apps/v1/routes/get-start/sse
# http://localhost:8686/sse
@app.service.route('/sse', methods=['GET'])
def sse():
    def generator():
        for i in range(10):
            yield f"hello again {i}"
            time.sleep(1)

    return flask.Response(generator(), mimetype='text/event-stream')


@app.prepare()
def prepare_model():
    volume = context.get_volume(VOLUME_NAME)

    model_path = os.path.join(volume.path, MODEL_FILE_NAME)
    if not os.path.exists(model_path):
        # download model file
        with open(model_path, 'wb') as f:
            f.write('hello world'.encode('utf-8'))

    # only in prepare mode push volume
    # to save gpu time (redundant sha256 checks)
    if context.is_prepare_mode:
        context.volume_manager.push(VOLUME_NAME)

    time.sleep(5)


@app.clear()
def clear():
    print('clear called')
