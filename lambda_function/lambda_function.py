import json
import os
import datetime
import logging
from typing import List, Dict, Any
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from mcstatus import JavaServer

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

######################################################################
#                         Helper Functions                           #
######################################################################

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()

        return super(DateTimeEncoder, self).default(o)
    
def send_command(command: str) -> None:
    ssm_client = boto3.client('ssm')
    ssm_client.put_parameter(
        Name='/mc_server/BOT_COMMAND',
        Value=command,
        Type='String',
        Overwrite=True
    )

def get_ssm_command() -> str:
    ssm_client = boto3.client('ssm', region_name='eu-west-2')

    param = ssm_client.get_parameter(Name="/mc_server/BOT_COMMAND", WithDecryption=True)
    command = param["Parameter"]["Value"]
    logger.debug(f"Retrieved SSM Comman: {command}")
    return command

def check_mc_server(ip: str, port: str) -> Dict[str, Any]:
    minecraft_server = JavaServer.lookup(f"{ip}:{port}")
    try:
        status = minecraft_server.status()
        return {
            'online': minecraft_server.ping() is not None,
            'players_online': status.players.online,
            'version': status.version.name
        }
    except Exception:
        logger.exception("Error while checking Minecraft server")
        return {
            'online': False,
            'players_online': 0,
            'version': 'unknown'
        }

def get_env_variables() -> Dict[str, str]:
    env_vars = ['MC_PORT', 'MC_SERVER_IP', 'CLUSTER', 'CONTAINER_NAME', 'DEFAULT_SUBNET_ID', 'DEFAULT_SECURITY_GROUP_ID', 
                'TF_USER_TOKEN', 'TAG_NAME', 'TAG_NAMESPACE', 'TAG_ENVIRONMENT']

    return {var: os.getenv(var) for var in env_vars}

######################################################################
#                           Fargate                                  #
######################################################################
def create_fargate_container(ecs_client, task_definition, cluster, container_name, network_configuration, environment_variables, tags):
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
        },
        tags=tags
    )
    task_arn = response["tasks"][0]["taskArn"]
    logger.debug(f"Created Fargate container with ARN: {task_arn}")
    return response["tasks"][0]["taskArn"]

def is_task_with_tags_exists(ecs_client, cluster, task_tags):
    response = ecs_client.list_tasks(cluster=cluster)

    for task_arn in response['taskArns']:
        task_details = ecs_client.describe_tasks(
            cluster=cluster,
            tasks=[task_arn],
            include=['TAGS'],  # Include tags in the response
        )

        for task in task_details['tasks']:
            if all(tag in task['tags'] for tag in task_tags):
                return True

    return False

def check_task_status(ecs_client, cluster, tags):
    # Convert tags to a dictionary for easier comparison
    tags_dict = {tag['key']: tag['value'] for tag in tags}

    # List all tasks in the cluster
    list_tasks_response = ecs_client.list_tasks(cluster=cluster)
    logger.info(f"list task response: {list_tasks_response}")

    for task_arn in list_tasks_response["taskArns"]:
        # Describe each task to get its tags
        describe_task_response = ecs_client.describe_tasks(cluster=cluster, tasks=[task_arn], include=['TAGS'])
        task = describe_task_response["tasks"][0]

        # Check if the task has the specified tags
        task_tags = {tag["key"]: tag["value"] for tag in task.get("tags", [])}
        # If the task has the specified tags, return its status
        if all(item in task_tags.items() for item in tags_dict.items()):
            logger.debug(f"Task Status: { task['lastStatus'] }")
            return task["lastStatus"]

    return None

######################################################################
#                       Lambda Handler                               #
######################################################################
def lambda_handler(event, context):
    try:
        command = json.loads(event["body"]).get("command")

        if not isinstance(command, str):
            raise ValueError('Command must be a string')

        envs = get_env_variables()
        ecs_client = boto3.client("ecs")
        environment_variables = [ {'name': 'TF_TOKEN_app_terraform_io', 'value': envs['TF_USER_TOKEN'] }]
        task_tags = [ {'key': key, 'value': value} for key, value in envs.items() if key.startswith('TAG_') ]

        task_running = is_task_with_tags_exists(ecs_client, envs['CLUSTER'], task_tags)

        if command in ('start', 'stop'):
            if task_running:
                task_status = check_task_status(ecs_client, envs['CLUSTER'], task_tags)
                return {
                    'statusCode': 200,
                    'body': json.dumps({'STATUS': task_status}, cls=DateTimeEncoder)
                }
            
            # Sends command to SSM param store
            send_command(command)

            fargate_network_configuration = {
                "awsvpcConfiguration": {
                    "subnets": [ envs['DEFAULT_SUBNET_ID'] ], 
                    "securityGroups": [ envs['DEFAULT_SECURITY_GROUP_ID'] ],
                    "assignPublicIp": "ENABLED"
                }   
            }
            task_arn = create_fargate_container(ecs_client, "minecraft_task_definition", envs['CLUSTER'], envs['CONTAINER_NAME'], fargate_network_configuration,
                                                environment_variables, task_tags)

            task_status = check_task_status(ecs_client, envs['CLUSTER'], task_tags)
            if task_status is None:
                raise Exception(f"Error running Starting Task: {task_arn}")

            response = {'STATUS': task_status}
        elif command == 'status':
            if task_running:
                task_status = check_task_status(ecs_client, envs['CLUSTER'], task_tags)
            else: # If there is no task_running, we check if the mc server is running
                mc_server_status = check_mc_server(envs["MC_SERVER_IP"], envs["MC_PORT"])

                if mc_server_status["online"]:
                    task_status = "MC_SERVER_UP"
                else:
                    task_status = "MC_SERVER_DOWN"

            response = {'STATUS': task_status, 'PREVIOUS_COMMAND': get_ssm_command()}
        else:
            raise ValueError(f"Invalid command: {command}")

        return {
            "statusCode": 200,
            "body": json.dumps(response, cls=DateTimeEncoder)
        }
    except (BotoCoreError, ClientError, Exception) as error:
        logger.exception(f"Error processing request: {str(error)}")
        return {
            "statusCode": 500,
            "body": json.dumps(str(error), cls=DateTimeEncoder)
        }
    except ValueError as error:
        logger.error(str(error))
        return {
            "statusCode": 400,
            "body": json.dumps(str(error), cls=DateTimeEncoder)
        }