# Serve Image + Variants via Cloudflare Images

!!! warning "Cloudflare Images is a Paid Service"

    [With]((https://developers.cloudflare.com/images/pricing/)) $5/month per _100k images stored_ and $1/month per _100k images delivered_, this shaves off time I'd otherwise spend rolling out my own image service to serve, format, modify images in the cloud.

## Why Cloudflare Images

See invocation to get a flexible server-generated image from Cloudflare:

```jinja title="Arbitrary variant"
<img src="{{profile.image_url|variant:'w=200'}}" alt="{{alt}}"> {# (1) #}
```

1. Creates `https://imagedelivery.net/.../w=200`: a flexible server-side variant

I can define a named variant, e.g. `avatar` to refer to _240x240_ pixels in the Cloudflare dashboard. This will ensure all images are sized with certain dimensions:

```jinja title="Named variant"
<img src="{{profile.image_url|variant:'avatar'}}" alt="{{alt}}">> {# (1) #}
```

1. Create `https://imagedelivery.net/.../avatar`: a pre-defined server-side variant

I find $60/year a justifiable price to pay to not handle image management on the web for all my projects.

## ImageField Storage

!!! note "Uses :simple-django: 4.2 Storage Class"

    See thin wrapper over Cloudflare Images v1 via separate library that [I built](https://www.mv3.dev/cloudflare-images#django). Relatedly, since this makes use of a third-party API for I/O, I use huey for this [background task](./background-tasks.md) of uploading the image.

When `ENV_NAME` is `dev`, user avatars will be stored in the `/src/mediafiles`. In non-`dev` environments, it will use the custom Storage Class.

```py title="profiles/models.py" linenums="1" hl_lines="1 8"
def select_storage(): # (1)
    if settings.ENV_NAME == "dev":
        return storages["default"]
    return storages["cloudflare_images"]

class Profile(TimeStampedModel):
    ...
    image = models.ImageField(storage=select_storage) # (2)
    ...
```

1. Actually `select_storage()` is found in _profiles/utils.py_ but is included here for context.
2. See this convention in :simple-django: [reference](https://docs.djangoproject.com/en/dev/topics/files/#using-a-callable).

??? "See definition of `LimitedStorageCloudflareImages` used by `select_storage()`"

    The definition is sourced from a [separate package I made](https://github.com/justmars/cloudflare-images/blob/main/cloudflare_images/django.py) for this purpose.

    ```py title="See cloudflare-images"
    class LimitedStorageCloudflareImages(Storage):
      def __init__(self):
          super().__init__()
          self.api = CloudflareImagesAPIv1()

      def __repr__(self):
          return "<LimitedToImagesStorageClassCloudflare>"

      def _open(self, name: str, mode="rb") -> File:
          return File(self.api.get(img_id=name), name=name)

      def _save(self, name: str, content: bytes) -> str:
          timestamp = datetime.datetime.now().isoformat()
          res = self.api.post(f"{name}/{timestamp}", content)
          return self.api.url(img_id=res.json()["result"]["id"])

      def get_valid_name(self, name):
          return name

      def get_available_name(self, name, max_length=None):
          return self.generate_filename(name)

      def generate_filename(self, filename):
          return filename

      def delete(self, name) -> httpx.Response:
          return self.api.delete(name)

      def exists(self, name: str) -> bool:
          res = self.api.get(name)
          if res.status_code == HTTPStatus.NOT_FOUND:
              return False
          elif res.status_code == HTTPStatus.OK:
              return True
          raise Exception("Image name found but http status code is not OK.")

      def listdir(self, path):
          raise NotImplementedError(
              "subclasses of Storage must provide a listdir() method"
          )

      def size(self, name: str):
          return len(self.api.get(name).content)

      def url(self, name: str):
          return self.api.url(name)

      def url_variant(self, name: str, variant: str):
          return self.api.url(name, variant)

      def get_accessed_time(self, name):
          raise NotImplementedError(
              "subclasses of Storage must provide a get_accessed_time() method"
          )

      def get_created_time(self, name):
          raise NotImplementedError(
              "subclasses of Storage must provide a get_created_time() method"
          )

      def get_modified_time(self, name):
          raise NotImplementedError(
              "subclasses of Storage must provide a get_modified_time() method"
          )
    ```

## Cloudflare Images Setup

It's a fairly straightforward process to create a Cloudflare Account.

Visit the _Cloudflare Images_ tab in the dashboard,  procure [secrets](https://www.mv3.dev/cloudflare-images/#api-v1) and add them into the `.env` file.

=== "Using plain-text"

    ```sh title="Values are stored in raw text format"
    CF_ACCT_ID=i-am-the-id
    CF_IMG_TOKEN=i-am-the-secret-for-the-id
    CF_IMG_HASH=part-of-url-of-every-image-served
    ```

=== "Using secret references"

    ```sh title="Actual values are stored in 1password"
    CF_ACCT_ID=op://dev/cf-img/acct_id
    CF_IMG_TOKEN=op://dev/cf-img/token
    CF_IMG_HASH=op://dev/cf-img/hash
    ```

    See same discussion on secret references in Social Auth [setup](./auth-social.md#storage).
