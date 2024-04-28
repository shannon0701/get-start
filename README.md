## 1. create an app
```shell
ever app create get-start
```
## 2. create secrets
>Optional, depending on whether the model and image require security certification

In this case, we will create two secrets for huggingface and quay.io 
```shell
ever secret create your-huggingface-secret-name --from-literal token=foo

ever secret create your-quay-io-secret-name \
  --from-literal username=foo \
  --from-literal password=bar 
```

## 3. create configmap
>Optional, but you can use configmap for adjust autoscaling after deploy 
```shell
ever configmap create autoscaling-config \ 
  --from-literal min_workers=1 \
  --from-literal max_workers=5 \
  --from-literal max_queue_size=2 \
  --from-literal scale_up_step=1 \
  --from-literal max_idle_time=60
```

## 4. write your app code in python
There is an example code in [app.py](app.py)

you could test in your local machine will following command
```shell
ever app run
```

## 6. prepare volume<span style="color:red">*</span>
Before your application cloud be deployed, you should construct your volume first, 
if your app use at least one volume.

For production environment, the volumes are very important,
you could call the following command to prepare it.

```shell
ever app prepare
```

This command line will call all functions who decorated by @app.prepare,
in these functions you should set up volume data before the app use it

## 7. build image
This step will build the container image, using two very simple files [Dockerfile](Dockerfile) and [image_builder.py](image_builder.py), 
and call the following command will compile the image and push them to your specified registry.
>The dependence of this step is docker and buildx installed on your machine. 
>Otherwise we will have further prompts to help you install them
```shell
ever image build
```

## 8. deploy image
The final step is to deploy your app to everai and keep it running.
```shell
ever app deploy
```

Now, you can make a test call for your app, in this example looks like
```shell
curl -X GET https://everai.expvent.com/api/apps/v1/routes/get-start/sse
```