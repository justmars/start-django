import httpx
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from django.db.models.fields.files import ImageFieldFile
from huey import signals
from huey.contrib.djhuey import signal, task


@task()
def background_store_img_url(url: str, field: ImageFieldFile, name: str):
    """Create a new file represented by `url`'s image. This new file object will be placed in storage (which is dependent on the `field`). See generally Django docs on File object [storage](https://docs.djangoproject.com/en/dev/ref/files/file/#additional-methods-on-files-attached-to-objects)."""  # noqa: E501
    res = httpx.get(url=url)
    content = ContentFile(res.content)
    return field.save(name=name, content=content)


@task()
def background_store_img_form(upload: UploadedFile, field: ImageFieldFile, name: str):
    """Similar to `background_store_img_url()` but uses an uploaded file from a form as opposed to a url."""  # noqa: E501
    return field.save(name=name, content=upload)


@signal(signals.SIGNAL_COMPLETE)
def handle_task_result(signal, task=background_store_img_form):
    """For sanity checks, mostly."""
    print(f"{task=} {signal=}")
