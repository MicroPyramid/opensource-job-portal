from boto.s3.connection import S3Connection
from boto.s3.key import Key
from django.conf import settings
import mimetypes
import boto


class AWS:

    def push_to_s3(self, file_obj, bucket_name=None, folder="", new_name=None, public_read=True):
        self.conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        filename = new_name
        content = file_obj.read()

        key = folder + new_name if new_name else filename

        bucket = self.conn.get_bucket(bucket_name=bucket_name)

        mime = mimetypes.guess_type(filename)[0]
        k = Key(bucket)
        k.key = key  # folder + filename
        k.set_metadata("Content-Type", mime)
        k.set_contents_from_string(content)
        if public_read:
            k.set_acl("public-read")

        key_buc = [k.key, bucket_name]
        return key_buc

    def cloudfront_invalidate(self, paths):
        c = boto.connect_cloudfront(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        c.create_invalidation_request(settings.CLOUDFRONT_ID, paths)
