from functools import lru_cache
import boto3

from .config import settings


@lru_cache
def get_dynamodb_resource():
    return boto3.resource("dynamodb", region_name=settings.aws_region)


@lru_cache
def get_sns_client():
    return boto3.client("sns", region_name=settings.aws_region)

# later i can add Kinesis client too