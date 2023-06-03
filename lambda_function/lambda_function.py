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

def check_task_status(ecs_client, cluster, tags):
    # List all tasks in the cluster
    list_tasks_response = ecs_client.list_tasks(cluster=cluster)

    for task_arn in list_tasks_response["taskArns"]:
        # Describe each task to get its tags
        describe_task_response = ecs_client.describe_tasks(cluster=cluster, tasks=[task_arn])
        task = describe_task_response["tasks"][0]

        # Check if the task has the specified tags
        task_tags = {tag["key"]: tag["value"] for tag in task.get("tags", [])}
        if all(item in task_tags.items() for item in tags.items()):
            # If the task has the specified tags, return its status
            return task["lastStatus"]

    # If no task with the specified tags is found, return None
    return None

def is_task_running(ecs_client, cluster, tags):
    response = ecs_client.list_tasks(
        cluster=cluster,
        desiredStatus='RUNNING',
    )

    for task_arn in response['taskArns']:
        task_details = ecs_client.describe_tasks(
            cluster=cluster,
            tasks=[task_arn],
        )

        for task in task_details['tasks']:
            for tag in task['tags']:
                if tag['key'] == 'Name' and tag['value'] == tags['Name']:
                    if tag['key'] == 'Namespace' and tag['value'] == tags['Namespace']:
                        if tag['key'] == 'Stage' and tag['value'] == tags['Stage']:
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

        # Task Tags allows us to search for the task
        task_tags = {
            'Name': os.environ["TAG_NAME"],
            'Namespace': os.environ["TAG_NAMESPACE"],
            'Stage': os.environ["TAG_ENVIRONMENT"],
        }
        task_running = is_task_running(ecs_client, cluster, task_tags)

        if (command == "start" or command == "stop"):
            # Check if task is running
            if task_running:
                print("Task is already running")
                return {
                    "statusCode": 400,
                    "body": json.dumps("Error: Task is already running", cls=DateTimeEncoder)
                }
            
            send_command(command) # sends command to SSM param store
            response = create_fargate_container(ecs_client, task_definition, cluster, container_name, network_configuration, environment_variables)
        elif (command == "status"):
            status = check_task_status(ecs_client, cluster, task_tags)
            
            if status is None:
                print("Error: No task with the specified tags was found")
                return {
                    "statusCode": 400,
                    "body": json.dumps("not running", cls=DateTimeEncoder)
                }

            response = { "task_status": status }
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