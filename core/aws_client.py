from functools import lru_cache

import boto3

from core.config import settings


@lru_cache
def get_dynamodb_resource():
    return boto3.resource("dynamodb", region_name=settings.aws_region)


@lru_cache
def get_sns_client():
    return boto3.client("sns", region_name=settings.aws_region)


def get_patients_table():
    return get_dynamodb_resource().Table(settings.patients_table)


def get_vitals_table():
    return get_dynamodb_resource().Table(settings.vitals_table)


def get_alerts_table():
    return get_dynamodb_resource().Table(settings.alerts_table)


def get_config_table():
    return get_dynamodb_resource().Table(settings.config_table)