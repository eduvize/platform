from typing import Tuple
import uuid
import boto3
import requests
import mimetypes
from sqlalchemy import Enum
from botocore.client import Config
from mypy_boto3_s3.service_resource import Bucket

from config import get_s3_access_key, get_s3_avatar_bucket, get_s3_endpoint, get_s3_public_endpoint, get_s3_secret_key

class StoragePurpose(Enum):
    AVATAR = 1
    INSTRUCTOR_ASSET = 2
    
storage_resource = boto3.resource(
    's3',
    endpoint_url=get_s3_endpoint(),
    aws_access_key_id=get_s3_access_key(),
    aws_secret_access_key=get_s3_secret_key(),
    config=Config(signature_version='s3v4'),
    region_name='us-east-1',
)

def get_bucket(purpose: StoragePurpose) -> Tuple[Bucket, str]:
    """
    Retrieves an S3 bucket client for a bucket chosen based on the provided purpose

    Args:
        purpose (StoragePurpose): The purpose of the bucket to retrieve

    Raises:
        ValueError: Invalid purpose provided

    Returns:
        Bucket: A tuple of Bucket and path prefix
    """
    if purpose == StoragePurpose.AVATAR:
        return storage_resource.Bucket(get_s3_avatar_bucket()), "avatars"
    elif purpose == StoragePurpose.INSTRUCTOR_ASSET:
        return storage_resource.Bucket(get_s3_avatar_bucket()), "instructor-assets"
    
    raise ValueError("Invalid file purpose provided, no bucket found")

async def import_from_url(
    url: str, 
    purpose: StoragePurpose
) -> str:
    """
    Downloads file from a URL and uploads it to the storage bucket for the provided purpose

    Args:
        url (str): The URL to download the file from
        purpose (StoragePurpose): The purpose of the bucket to upload the file to

    Returns:
        str: The object ID of the uploaded file in the storage bucket
    """
    response = requests.get(url)
    response.raise_for_status()
    
    (bucket, prefix) = get_bucket(purpose)
    extension = mimetypes.guess_extension(response.headers['content-type'])
    
    if not extension:
        extension = ".bin"
        
    object_id = get_random_key(extension)
    
    bucket.put_object(
        Key=f"{prefix}/{object_id}",
        Body=response.content,
        ContentType=response.headers['content-type'],
        ACL="public-read"
    )
    
    return object_id

def get_public_object_url(
    purpose: StoragePurpose, 
    object_id: str
) -> str:
    """
    Returns a public access URL for an object in the storage bucket for the provided purpose

    Args:
        purpose (StoragePurpose): The purpose of the bucket to retrieve
        object_id (str): The ID of the object to retrieve

    Returns:
        str: A publicly accessible URL for the object
    """
    (bucket, prefix) = get_bucket(purpose)
    return f"{get_s3_public_endpoint()}/{bucket.name}/{prefix}/{object_id}"

async def upload_object(
    purpose: StoragePurpose, 
    data: bytes, 
    extension: str
) -> str:
    """
    Uploads an object to the storage bucket for the provided purpose

    Args:
        purpose (StoragePurpose): The purpose of the bucket to upload the object to
        data (bytes): The data to upload
        extension (str): The extension of the object (including the dot)
        
    Returns:
        str: The object ID of the uploaded file in the storage bucket
    """
    
    (bucket, prefix) = get_bucket(purpose)
    
    (content_type, _) = mimetypes.guess_type(extension)
    
    if not content_type:
        content_type = "application/octet-stream"
    
    object_id = get_random_key(extension)
    
    bucket.put_object(
        Key=f"{prefix}/{object_id}",
        Body=data,
        ContentType=content_type,
        ACL="public-read"
    )
    
    return object_id

def object_exists(
    bucket: Bucket, 
    key: str
) -> bool:
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

def get_random_key(extension: str = "") -> str:
    return f"{uuid.uuid4().hex}{extension}"