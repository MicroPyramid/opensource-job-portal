import boto3
from django.conf import settings
import mimetypes


class AWS:
    def push_to_s3(
        self, file_obj, bucket_name=None, folder="", new_name=None, public_read=True
    ):
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        filename = new_name
        content = file_obj.read()
        key = folder + new_name if new_name else filename
        
        mime = mimetypes.guess_type(filename)[0]
        
        # Upload the file to S3
        extra_args = {}
        if mime:
            extra_args['ContentType'] = mime
        if public_read:
            extra_args['ACL'] = 'public-read'
            
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=content,
            **extra_args
        )

        key_buc = [key, bucket_name]
        return key_buc

    def cloudfront_invalidate(self, paths):
        cloudfront_client = boto3.client(
            'cloudfront',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        # Note: You'll need to provide the distribution ID
        # This is a placeholder implementation
        if hasattr(settings, 'CLOUDFRONT_DISTRIBUTION_ID'):
            cloudfront_client.create_invalidation(
                DistributionId=settings.CLOUDFRONT_DISTRIBUTION_ID,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(paths),
                        'Items': paths
                    },
                    'CallerReference': str(hash(tuple(paths)))
                }
            )
