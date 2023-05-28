import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import os
import tempfile
import datetime

# Helper Funfctions
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()

        return super(DateTimeEncoder, self).default(o)
    
def send_command(command):
    ssm_client = boto3.client('ssm')
    ssm_client.put_parameter(
        Name='/mc_server/BOT_COMMAND',
        Value=command,
        Type='String',
        Overwrite=True
    )


######################################################################
#                           Fargate                                  #
######################################################################
def create_fargate_container(ecs_client, task_definition, cluster, container_name, network_configuration, environment_variables):
    response = ecs_client.run_task(
        cluster=cluster,
        launchType="FARGATE",
        taskDefinition=task_definition,
        count=1,
        platformVersion="LATEST",
        networkConfiguration=network_configuration,
        overrides={
            "containerOverrides": [{
                "name": container_name,
                "environment": environment_variables
            }]
        }
    )
    task_arn = response["tasks"][0]["taskArn"]
    print(f"Created Fargate container with ARN: {task_arn}")
    return task_arn

def destroy_fargate_container(ecs_client, cluster, task_arn):
    response = ecs_client.stop_task(
        cluster=cluster,
        task=task_arn
    )
    
    print(f"Destroyed Fargate container with ARN: {task_arn}")
    return response

def check_task_status(ecs_client, cluster, task):
    ecs_client = boto3.client("ecs")
    response = ecs_client.describe_tasks(
        cluster=cluster,
        tasks=[task]
    )
    
    for task in response["tasks"]:
        print(f"Task {task['taskArn']} is {task['lastStatus']}")

    return response

######################################################################
#                       Lambda Handler                               #
######################################################################
def lambda_handler(event, context):
    response = None
    try:
        # Extract request body
        command = json.loads(event["body"]).get("command")
        task_arn = json.loads(event["body"]).get("task_arn")

        send_command(command) # sends command to SSM param store

        # ECS Fargate Config
        ecs_client = boto3.client("ecs")
        task_definition = "minecraft_task_definition"
        cluster = os.getenv("CLUSTER")
        container_name = os.getenv("CONTAINER_NAME")
        subnet_id = os.getenv("DEFAULT_SUBNET_ID")
        security_group_id = os.getenv("DEFAULT_SECURITY_GROUP_ID")
        network_configuration = {
            "awsvpcConfiguration": {
                "subnets": [ subnet_id ],  # replace with your subnet
                "securityGroups": [ security_group_id],  # replace with your security group
                "assignPublicIp": "ENABLED"
            }
        }
        environment_variables = [
            {
                "name": "task_arn",
                "value": f"{task_arn}" 
            }, 
            {
                "name": "TF_TOKEN_app_terraform_io",
                "value": os.environ["TF_USER_TOKEN"]
            }, 
        ]

        if (command == "start"):
            response = create_fargate_container(ecs_client, task_definition, cluster, container_name, network_configuration, environment_variables)
        elif (command == "status"):
            # Check if task_arn is not null
            if not task_arn:
                print("Error: task_arn must not be null when checking task status")
                return {
                    "statusCode": 400,
                    "body": json.dumps("Error: task_arn must not be null when checking task status", cls=DateTimeEncoder)
                }
            
            response = check_task_status(ecs_client, cluster, task_arn)
        else:
            raise ValueError("Invalid command: " + command)

    except (BotoCoreError, ClientError) as error:
        # If there was an error, return an HTTP 500 response with the error message
        print(f"Error running Fargate task: {error}")
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error running Fargate task: {error}", cls=DateTimeEncoder)
        }
    
    except ValueError as error:
        # Handle the ValueError here
        error_message = str(error)
        return {
            "statusCode": 400,
            "body": json.dumps(error_message, cls=DateTimeEncoder)
        }

    return {
        "statusCode": 200,
        "body": json.dumps(response, cls=DateTimeEncoder)
    }