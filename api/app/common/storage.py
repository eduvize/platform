import boto3
from sqlalchemy import Enum
from botocore.client import Config
from mypy_boto3_s3.service_resource import Bucket

from config import get_s3_access_key, get_s3_avatar_bucket, get_s3_endpoint, get_s3_public_endpoint, get_s3_secret_key

class StoragePurpose(Enum):
    AVATAR = 1
    
storage_resource = boto3.resource(
    's3',
    endpoint_url=get_s3_endpoint(),
    aws_access_key_id=get_s3_access_key(),
    aws_secret_access_key=get_s3_secret_key(),
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

def get_bucket(purpose: StoragePurpose) -> Bucket:
    """
    Retrieves an S3 bucket client for a bucket chosen based on the provided purpose

    Args:
        purpose (StoragePurpose): The purpose of the bucket to retrieve

    Raises:
        ValueError: Invalid purpose provided

    Returns:
        Bucket: An S3 Bucket to interact with
    """
    if purpose == StoragePurpose.AVATAR:
        return storage_resource.Bucket(get_s3_avatar_bucket())
    
    raise ValueError("Invalid file purpose provided, no bucket found")

def get_public_object_url(purpose: StoragePurpose, object_id: str) -> str:
    """
    Returns a public access URL for an object in the storage bucket for the provided purpose

    Args:
        purpose (StoragePurpose): The purpose of the bucket to retrieve
        object_id (str): The ID of the object to retrieve

    Returns:
        str: A publicly accessible URL for the object
    """
    bucket = get_bucket(purpose)
    return f"{get_s3_public_endpoint()}/{bucket.name}/{object_id}"

def object_exists(bucket: Bucket, key: str) -> bool:
    """
    Helper function for determining whether an object exists in a bucket or not

    Args:
        bucket (Bucket): The bucket to check for the object in
        key (str): The key of the object to check for

    Returns:
        bool: Whether the object exists or not
    """
    lst = bucket.objects.filter(Prefix=key).limit(1)
    
    return bool(list(lst))