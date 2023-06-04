import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import os
import tempfile
import datetime
import random

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

def get_ssm_command():
    ssm_client = boto3.client('ssm', region_name='eu-west-2')

    param = ssm_client.get_parameter(Name="/mc_server/BOT_COMMAND", WithDecryption=True)
    contents = param["Parameter"]["Value"]
        
    return contents

def state_bot_reply(command, state):
    bot_reply = ""

    STARTING_REPLIES = [
        "Your Minecraft server is under construction! Please hang in there, it should be ready in about 6-7 minutes.",
        "We're hard at work setting up your Minecraft server. Expect to be playing in just 6-7 minutes!",
        "Minecraft server coming up! Sit tight, we'll have it ready for you in roughly 6-7 minutes."
    ]

    ACTIVATING_REPLIES = [
        "Initiating server setup. Your Minecraft world is being created!",
        "Hang tight! We're in the process of creating your Minecraft world.",
        "Just a moment more. We're bringing your Minecraft server to life!"
    ]

    RUNNING_REPLIES = [
        "Your Minecraft server is being prepared. Please wait while we set up the infrastructure for your adventure!",
        "Great news! We're currently setting up your Minecraft server. Get ready to embark on your journey soon!",
        "Your Minecraft server is currently being provisioned. It won't be long before you can start your exciting adventure!"
    ]

    STOPPING_REPLIES = [
        "We're wrapping up server setup. Your Minecraft world is almost ready!",
        "Just a few final touches and your Minecraft world will be ready.",
        "Almost there! Your Minecraft world is nearly ready for you."
    ]

    STOPPED_REPLIES = [
        "Minecraft server setup complete. Welcome to your new world!",
        "Server setup is done! Your Minecraft world awaits.",
        "All done! Your Minecraft server is ready for exploration."
    ]

    STOP_PROVISIONING_REPLIES = [
        "We're preparing to take your Minecraft server offline, please wait.",
        "Starting the shutdown process for your Minecraft server, please hold on.",
        "We're beginning the process to bring your Minecraft server offline."
    ]

    STOP_ACTIVATING_REPLIES = [
        "Initiating server shutdown. Your Minecraft world is being saved.",
        "Starting the process to safely shut down your Minecraft world.",
        "Your Minecraft server is preparing to go offline. We're saving your world data."
    ]

    STOP_RUNNING_REPLIES = [
        "Your Minecraft server is currently shutting down.",
        "Server shutdown in progress. Your Minecraft world will be ready for you when you return.",
        "Your Minecraft server is on its way offline. We're making sure everything is saved for next time."
    ]

    if command == "start":
        if state in ["PROVISIONING", "PENDING"]:
            bot_reply = random.choice(STARTING_REPLIES)
        elif state == "ACTIVATING":
            bot_reply = random.choice(ACTIVATING_REPLIES)
        elif state == "RUNNING":
            bot_reply = random.choice(RUNNING_REPLIES)
        elif state in ["DEACTIVATING", "STOPPING"]:
            bot_reply = random.choice(STOPPING_REPLIES)
        elif state == "STOPPED":
            bot_reply = random.choice(STOPPED_REPLIES)
        else:
            bot_reply = "Hmm, we're not sure what's happening. Please check back soon."
    elif command == "stop":
        if state in ["PROVISIONING", "PENDING"]:
            bot_reply = random.choice(STOP_PROVISIONING_REPLIES)
        elif state == "ACTIVATING":
            bot_reply = random.choice(STOP_ACTIVATING_REPLIES)
        elif state == "RUNNING":
            bot_reply = random.choice(STOP_RUNNING_REPLIES)
        else:
            bot_reply = "Hmm, we're not sure what's happening. Please check back soon."

    return bot_reply

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
                print("Task is already running")
                response = { "BOT_REPLY": "TASK IS ALREADY RUNNING"}
                return
            
            send_command(command) # sends command to SSM param store
            task_arn = create_fargate_container(ecs_client, task_definition, cluster, container_name, network_configuration, environment_variables, task_tags)

            if command == "start":
                bot_reply = "Your Minecraft server is under construction! Please hang in there, it should be ready in about 6-7 minutes."
            if command == "stop":
                bot_reply = "We're preparing to take your Minecraft server offline, please wait."

            response = { "TASK_ARN": task_arn, "BOT_REPLY": bot_reply }
        elif (command == "status"):
            previous_command = get_ssm_command()
            print(f"previous_command {previous_command}")
            status = None

            if task_running:
                status = check_task_status(ecs_client, cluster, task_tags)
                print(f"check_task_status: {status}")
            
            if status is None:
                print("No task with the specified tags was found")
                response = {"STATUS": status, "BOT_REPLY": "NOT RUNNING"}
            else:
                bot_reply = state_bot_reply(previous_command, status)
                response = {"STATUS": status, "BOT_REPLY": bot_reply}
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