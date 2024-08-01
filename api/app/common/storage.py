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
    if purpose == StoragePurpose.AVATAR:
        return storage_resource.Bucket(get_s3_avatar_bucket())
    
    raise ValueError("Invalid file purpose provided, no bucket found")

def get_public_object_url(purpose: StoragePurpose, object_id: str) -> str:
    bucket = get_bucket(purpose)
    return f"{get_s3_public_endpoint()}/{bucket.name}/{object_id}"

def object_exists(bucket: Bucket, key: str) -> bool:
    lst = bucket.objects.filter(Prefix=key).limit(1)
    
    return bool(list(lst))