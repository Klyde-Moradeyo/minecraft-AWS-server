import json
import os
import time
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
    
def send_command(command: str, ssm_path: str) -> None:
    ssm_client = boto3.client('ssm')
    ssm_client.put_parameter(
        Name=f"/{ssm_path}",
        Value=command,
        Type='String',
        Overwrite=True
    )

def get_ssm_command(ssm_path: str) -> str:
    ssm_client = boto3.client('ssm', region_name='eu-west-2')

    param = ssm_client.get_parameter(Name=f"/{ssm_path}", WithDecryption=True)
    command = param["Parameter"]["Value"]
    logger.debug(f"Retrieved SSM Comman: {command}")
    return command

def check_mc_server(ip: str, port: str) -> Dict[str, Any]:
    try:
        minecraft_server = JavaServer.lookup(f"{ip}:{port}")

        status = minecraft_server.status()
        return {
            'online': minecraft_server.ping() is not None,
            'players_online': status.players.online,
            'version': status.version.name
        }
    except Exception:
        logger.warning("Warning: Could not check the Minecraft server. Maybe its offline?")
        return {
            'online': False,
            'players_online': 0,
            'version': 'unknown'
        }

def get_env_variables() -> Dict[str, Any]:
    # List of required environment variables
    required_vars = [
        'MC_PORT', 'MC_SERVER_IP', 'CLUSTER', 'CONTAINER_NAME', 
        'SUBNET_ID', 'SECURITY_GROUP_ID', 'TF_USER_TOKEN', 'BOT_COMMAND_NAME',
        'TASK_DEFINITION_NAME', 'GIT_PRIVATE_KEY', 'EC2_PRIVATE_KEY'
    ]

    env_vars = {var: os.getenv(var) for var in required_vars}

    # Decode the TAGS_JSON environment variable
    tags_json = os.getenv('TAGS_JSON')
    if not tags_json:
        raise ValueError("Missing environment variable: TAGS_JSON")

    try:
        tags = json.loads(tags_json)
    except json.JSONDecodeError:
        raise ValueError("Error decoding TAGS_JSON. Ensure it's a valid JSON string.")

    # Add the Tags
    env_vars.update({
        'TAG_NAME': tags.get('Name'),
        'TAG_NAMESPACE': tags.get('Namespace'),
        'TAG_ENVIRONMENT': tags.get('Stage'),
    })

    # Check if any required environment variable is missing
    missing_vars = [key for key, value in env_vars.items() if value is None]
    if missing_vars:
        raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")
    
    for key, value in env_vars.items():
        logger.debug(f"{key}: {value}")

    return env_vars


def seconds_to_minutes(seconds: int) -> float:
    if not isinstance(seconds, int) or seconds < 0:
        raise ValueError("Input seconds should be a non-negative integer.")
    
    return seconds / 60.0

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

def is_task_with_tags_exists(ecs_client, cluster, desired_tags):
    # Fetch tasks from the given cluster
    try:
        tasks_response = ecs_client.list_tasks(cluster=cluster)
    except Exception as e:
        logger.error(f"Error fetching tasks from cluster {cluster}: {e}")
        return False

    # Iterate over each task ARN retrieved
    for task_arn in tasks_response.get('taskArns'):
        # Try to get the details of the current task, including its tags
        try:
            current_task_details = ecs_client.describe_tasks(
                cluster=cluster,
                tasks=[task_arn],
                include=['TAGS'],
            )
        except Exception as e:
            logger.error(f"Error fetching details for task {task_arn} in cluster {cluster}: {e}")
            return False

        for task_data in current_task_details.get('tasks'):
            tag_match_count = 0 

            # Compare each desired tag against the task's tags
            for tag_to_check in desired_tags:
                if tag_to_check['key'] == 'TAG_RUNNING_COMMAND': # For the 'TAG_RUNNING_COMMAND', only check the key's presence. We dont care about the value
                    if any(existing_tag['key'] == tag_to_check['key'] for existing_tag in task_data.get('tags')):
                        tag_match_count += 1
                else: # For other tags, check both the key and value
                    if tag_to_check in task_data.get('tags'):
                        tag_match_count += 1

            # If all desired tags are found within the task's tags, return True
            if tag_match_count == len(desired_tags):
                logger.info(f"Located task with ARN {task_arn} matching the specified tags.")
                return True

    # If no tasks matched the provided tags
    logger.info(f"No tasks matching the provided tags were found in cluster {cluster}.")
    return False

def check_task_status(ecs_client, cluster, tags):
    # List all tasks in the cluster
    try:
        list_tasks_response = ecs_client.list_tasks(cluster=cluster)
    except Exception as e:
        logger.error(f"Error fetching tasks from cluster {cluster}: {e}")
        return None

    logger.info(f"List task response: {list_tasks_response}")

    for task_arn in list_tasks_response.get("taskArns", []):
        # Describe each task to get its tags
        try:
            describe_task_response = ecs_client.describe_tasks(cluster=cluster, tasks=[task_arn], include=['TAGS'])
        except Exception as e:
            logger.warning(f"Error fetching details for task {task_arn} in cluster {cluster}: {e}")
            continue
        
        task = describe_task_response["tasks"][0]

        tag_match_count = 0
        for tag_to_check in tags:
            if tag_to_check['key'] == 'TAG_RUNNING_COMMAND': 
                # For the 'TAG_RUNNING_COMMAND', only check the key's presence. We don't care about the value.
                if any(existing_tag['key'] == tag_to_check['key'] for existing_tag in task.get('tags', [])):
                    tag_match_count += 1
            else: 
                # For other tags, check both the key and value.
                if tag_to_check in task.get('tags', []):
                    tag_match_count += 1

        # If all tags match, return the task's status
        if tag_match_count == len(tags):
            logger.debug(f"Task Status: { task['lastStatus'] }")
            return task["lastStatus"]

    logger.info(f"No tasks matched the provided tags: {tags}.")
    return None

######################################################################
#                       Lambda Handler                               #
######################################################################
def lambda_handler(event, context):
    try:
        # Environment Vars
        envs = get_env_variables()

        # Inputs
        parsed_body = json.loads(event["body"])
        recursion_count = parsed_body.get("recursion_count", 0)
        command = parsed_body.get("command")
        envs['TAG_RUNNING_COMMAND'] = command

        # Log Input
        logger.info(f"COMMAND: {command} | Recursion Count: {recursion_count}")
        
        # to do: We will need a error for sent to admin when recursion reaches a certain amount e.g 5 times
        if recursion_count == 3:
            logging.error(f"RECURSION LIMIT HIT: {recursion_count}")
            raise TimeoutError

        if not isinstance(command, str):
            raise ValueError('Command must be a string')

        ecs_client = boto3.client("ecs")
        environment_variables = [ 
            {'name': 'TF_USER_TOKEN', 'value': envs['TF_USER_TOKEN'] },
            {'name': 'GIT_PRIVATE_KEY', 'value': envs['GIT_PRIVATE_KEY'] },
            {'name': 'EC2_PRIVATE_KEY', 'value': envs['EC2_PRIVATE_KEY'] },
            ]
        task_tags = [ {'key': key, 'value': value} for key, value in envs.items() if key.startswith('TAG_') ]
        fargate_network_configuration = {
            "awsvpcConfiguration": {
                "subnets": [ envs['SUBNET_ID'] ], 
                "securityGroups": [ envs['SECURITY_GROUP_ID'] ],
                "assignPublicIp": "ENABLED"
            }   
        }

        task_running = is_task_with_tags_exists(ecs_client, envs['CLUSTER'], task_tags)
 
        mc_server_status = check_mc_server(envs["MC_SERVER_IP"], envs["MC_PORT"])

        if command == "mc_world_archive":
            # Wait for task to finish running then schedule task
            if task_running:
                check_interval = 60
                time_limit = 600
                time_elapsed = 0 # counter
                
                logging.info(f"waiting for {seconds_to_minutes(time_limit)} minutes")
                while time_elapsed < time_limit:  
                    task_running = is_task_with_tags_exists(ecs_client, envs['CLUSTER'], task_tags)
                    if not task_running: # Launch new Fargate task and exit if there is no task running
                        send_command(command, envs["BOT_COMMAND_NAME"])
                        task_arn = create_fargate_container(ecs_client, envs['TASK_DEFINITION_NAME'], envs['CLUSTER'], envs['CONTAINER_NAME'], fargate_network_configuration,
                                                            environment_variables, task_tags)
                        logger.info(f"New Fargate task launched: {task_arn}")

                        task_status = check_task_status(ecs_client, envs['CLUSTER'], task_tags)
                        if task_status is None:
                            raise Exception(f"Error running Starting Task: {task_arn}")
                        
                        response = { "STATUS": f"MC_WORLD_ARCHIVE_{task_status}", "INFO": f"New Fargate task launched: {task_arn}" }
                        break
                    time.sleep(check_interval)  # check every 5 seconds
                    time_elapsed += check_interval
                    logging.info(f"time elapsed: {time_elapsed} seconds")

                if time_elapsed >= time_limit:
                    logger.warning(f"Fargate task still running after {seconds_to_minutes(time_elapsed)} minutes.")

                # Improvement: Retrigger Lambda after a period of time if the fargate task hasnt been srarted after the specified time
                response = { "STATUS": f"MC_WORLD_ARCHIVE_FAILED_START", "INFO": f"Timed out" }
            else:
                logger.info(f"Else statement")
                send_command(command, envs["BOT_COMMAND_NAME"])
                task_arn = create_fargate_container(ecs_client, envs['TASK_DEFINITION_NAME'], envs['CLUSTER'], envs['CONTAINER_NAME'], fargate_network_configuration,
                                                    environment_variables, task_tags)
                logger.info(f"New Fargate task launched: {task_arn}")
                task_status = check_task_status(ecs_client, envs['CLUSTER'], task_tags)
                if task_status is None:
                    raise Exception(f"Error running Starting Task: {task_arn}")
                
                response = { "STATUS": f"MC_WORLD_ARCHIVE_{task_status}", "INFO": f"New Fargate task launched: {task_arn}" }
        elif command in ('start', 'stop'):
            if command == "stop" and not mc_server_status["online"]:
                task_status = "MC_SERVER_DOWN"
                return {
                    'statusCode': 200,
                    'body': json.dumps({'STATUS': task_status}, cls=DateTimeEncoder)
                }
            
            if task_running:
                task_status = check_task_status(ecs_client, envs['CLUSTER'], task_tags)
                return {
                    'statusCode': 200,
                    'body': json.dumps({'STATUS': task_status}, cls=DateTimeEncoder)
                }
            
            # Sends command to SSM param store
            send_command(command, envs["BOT_COMMAND_NAME"])

            task_arn = create_fargate_container(ecs_client, envs['TASK_DEFINITION_NAME'], envs['CLUSTER'], envs['CONTAINER_NAME'], fargate_network_configuration,
                                                environment_variables, task_tags)

            task_status = check_task_status(ecs_client, envs['CLUSTER'], task_tags)
            if task_status is None:
                raise Exception(f"Error running Starting Task: {task_arn}")

            response = {'STATUS': task_status}
        elif command == 'status':
            if task_running:
                task_status = check_task_status(ecs_client, envs['CLUSTER'], task_tags)
            else: # If there is no task_running, we check if the mc server is running
                if mc_server_status["online"]:
                    task_status = "MC_SERVER_UP"
                else:
                    task_status = "MC_SERVER_DOWN"

            response = {'STATUS': task_status, 'PREVIOUS_COMMAND': get_ssm_command(envs["BOT_COMMAND_NAME"])}
        else:
            raise ValueError(f"Invalid command: {command}")

        return {
            "statusCode": 200,
            "body": json.dumps(response, cls=DateTimeEncoder)
        }
    except TimeoutError as error:
        logger.error("Timeout occurred", extra={
            "error": str(error),
            "recursion_count": recursion_count
        })
        return {
            "statusCode": 408,
            "body": json.dumps({"error": str(error)}, cls=DateTimeEncoder) 
        }

    except ValueError as error:
        logger.error("Value error occurred", extra={
            "error": str(error),
        })
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(error)}, cls=DateTimeEncoder)
        }

    except (BotoCoreError, ClientError) as error:
        logger.exception("Boto3 related error occurred", extra={
            "error": str(error),
        })
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(error)}, cls=DateTimeEncoder)
        }

    except Exception as error:
        logger.exception("Unhandled exception occurred", extra={
            "error": str(error),
        })
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(error)}, cls=DateTimeEncoder)
        }
    
# For testing 
# if __name__ == '__main__':
#     event = {
#         "body": { 
#             "commnad": "status"
#         }
#     }
#     # for key, value in os.environ.items():
#     #     print(f"{key}={value}")
#     result = lambda_handler(event, None)
#     print(result)
