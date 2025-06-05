import boto3
from django.conf import settings
import mimetypes


class S3Connection:
    """
    A boto3-based replacement for tinys3.Connection
    """
    
    def __init__(self, access_key_id, secret_access_key):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key
        )
    
    def upload(self, key, file_obj, bucket_name, public=True):
        """
        Upload a file to S3 bucket using boto3
        
        Args:
            key (str): The S3 key (path) for the file
            file_obj: File object or file-like object to upload
            bucket_name (str): Name of the S3 bucket
            public (bool): Whether to make the file publicly readable
        
        Returns:
            str: The S3 key of the uploaded file
        """
        # Determine content type
        content_type = mimetypes.guess_type(key)[0]
        
        # Prepare upload arguments
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        
        if public:
            extra_args['ACL'] = 'public-read'
        
        # Upload the file
        if hasattr(file_obj, 'read'):
            # File-like object
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=file_obj.read(),
                **extra_args
            )
        else:
            # Assume it's already bytes or string content
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=file_obj,
                **extra_args
            )
        
        return key
