import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import os
import tempfile
import datetime
import logging
from mcstatus import JavaServer

logging.basicConfig(level=logging.DEBUG)

######################################################################
#                         Helper Functions                           #
######################################################################
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

def get_ssm_command():
    ssm_client = boto3.client('ssm', region_name='eu-west-2')

    param = ssm_client.get_parameter(Name="/mc_server/BOT_COMMAND", WithDecryption=True)
    contents = param["Parameter"]["Value"]
        
    return contents

def check_mc_server(ip, port):
    minecraft_server = JavaServer.lookup(f"{ip}:{port}")
    try:
        status = minecraft_server.status()
        return {
            'online': minecraft_server.ping() is not None,
            'players_online': status.players.online,
            'version': status.version.name
        }
    except Exception:
        return {
            'online': False,
            'players_online': 0,
            'version': 'unknown'
        }

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
    print(response)
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

def check_task_status(ecs_client, cluster, tags):
    # Convert tags to a dictionary for easier comparison
    tags_dict = {tag['key']: tag['value'] for tag in tags}

    # List all tasks in the cluster
    list_tasks_response = ecs_client.list_tasks(cluster=cluster)
    print(f"list task response: {list_tasks_response}")

    for task_arn in list_tasks_response["taskArns"]:
        # Describe each task to get its tags
        describe_task_response = ecs_client.describe_tasks(cluster=cluster, tasks=[task_arn], include=['TAGS'])
        print(f"describe task response: {describe_task_response}")
        task = describe_task_response["tasks"][0]
        print(f"task: {task}")

        # Check if the task has the specified tags
        task_tags = {tag["key"]: tag["value"] for tag in task.get("tags", [])}
        if all(item in task_tags.items() for item in tags_dict.items()):
            # If the task has the specified tags, return its status
            return task["lastStatus"]

    # If no task with the specified tags is found, return None
    return None

def is_task_with_tags_exists(ecs_client, cluster, task_tags):
    print(f"PARAMS: {ecs_client}, {cluster}, {task_tags}")

    response = ecs_client.list_tasks(
        cluster=cluster,
    )
    print(f"RESPONSE: {response}")

    for task_arn in response['taskArns']:
        print(f"TASK ARNS: {task_arn}")
        task_details = ecs_client.describe_tasks(
            cluster=cluster,
            tasks=[task_arn],
            include=['TAGS'],  # Include tags in the response
        )

        for task in task_details['tasks']:
            print(f"task_details: {task}")
            if all(tag in task['tags'] for tag in task_tags):
                print("PASS")
                return True

    return False

######################################################################
#                       Lambda Handler                               #
######################################################################
def lambda_handler(event, context):
    response = None
    try:
        # Extract request body
        command = json.loads(event["body"]).get("command")
        if not isinstance(command, str):
            raise ValueError('Command must be a string')
        
        # Initilize bot response
        service_status = None

        MC_PORT = os.environ["MC_PORT"]
        MC_SERVER_IP = os.environ["MC_SERVER_IP"]

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
                "name": "TF_TOKEN_app_terraform_io",
                "value": os.environ["TF_USER_TOKEN"]
            }, 
        ]
        task_tags = [
            {
                "key": "Name",
                "value": os.environ["TAG_NAME"]
            },
            {
                "key": "Namespace",
                "value": os.environ["TAG_NAMESPACE"]
            },
            {
                "key": "Stage",
                "value": os.environ["TAG_ENVIRONMENT"]
            }
        ]

        task_running = is_task_with_tags_exists(ecs_client, cluster, task_tags)
        print(f"TASK_RUNNING: {task_running}")

        if (command == "start" or command == "stop"):
            # Check if task is running
            if task_running:
                task_status = check_task_status(ecs_client, cluster, task_tags)
                response = { "STATUS": task_status}
                return
            
            # Sends command to SSM param store
            send_command(command) 

            # Start Fargate Container
            task_arn = create_fargate_container(ecs_client, task_definition, cluster, container_name, network_configuration, environment_variables, task_tags)

            task_status = check_task_status(ecs_client, cluster, task_tags)
            if task_status is not None:
                response = { "STATUS": task_status }
            else:
                err_msg = f"Error running Starting Task: {task_arn}"
                logging.info(err_msg)
                raise Exception(err_msg)
        elif (command == "status"):
            status = None
            previous_command = get_ssm_command()

            logging.info(f"previous_command: {previous_command}")

            if task_running:
                task_status = check_task_status(ecs_client, cluster, task_tags)
                logging.info(f"check_task_status: {task_status}")
            else:
                # If there is no task_running, we check if the mc server is running
                mc_server_status = check_mc_server(MC_SERVER_IP, MC_PORT)

                if mc_server_status["online"]:
                    task_status = "MC_SERVER_UP"
                else:
                    task_status = "MC_SERVER_DOWN"
            
            response = { "STATUS": task_status, "PREVIOUS_COMMAND": previous_command }
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
