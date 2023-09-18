import os
import boto3
from logger import setup_logging

# Setting up logging
logger = setup_logging()

def get_ssm_param(param_name):
    """
    Fetch the parameter value from AWS Systems Manager (SSM) Parameter Store.
    """
    ssm_client = boto3.client('ssm')
    response = ssm_client.get_parameter(
        Name=param_name ,
        WithDecryption=True
    )
    return response['Parameter']['Value']

def put_ssm_param(param_name, param_value, param_type="SecureString"):
    """
    Put the specified parameter value into AWS Systems Manager (SSM) Parameter Store.
    """
    ssm_client = boto3.client('ssm', region_name='eu-west-2')

    ssm_client.put_parameter(
        Name=param_name,
        Value=param_value,
        Type=param_type,
        Overwrite=True
    )


def get_region():
    """
    Fetch the current region from boto3
    """
    return boto3.session.Session().region_name