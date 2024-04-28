from everai.image import Builder

IMAGE = 'quay.io/mc_jones/get-start:v0.0.30'


def pre_build():
    ...


def post_build():
    ...


image_builder = Builder.from_dockerfile(
    'Dockerfile',
    labels={
        "any-your-key": "value",
    },
    repository=IMAGE,
    platform=['linux/arm64', 'linux/x86_64'],
).pre_build(pre_build).post_build(post_build)
