import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import os

def create_fargate_container(ecs_client, task_definition, cluster, network_configuration, environment_variables):
    response = ecs_client.run_task(
        cluster=cluster,
        launchType="FARGATE",
        taskDefinition=task_definition,
        count=1,
        platformVersion="LATEST",
        networkConfiguration=network_configuration,
        overrides={
            "containerOverrides": [{
                "name": task_definition,
                "environment": environment_variables
            }]
        }
    )
    task_arn = response["tasks"][0]["taskArn"]
    print(f"Created Fargate container with ARN: {task_arn}")
    task_arn = create_fargate_container(task_definition, cluster, network_configuration, environment_variables)
    return task_arn

def destroy_fargate_container(ecs_client, cluster, task_arn):
    response = ecs_client.stop_task(
        cluster=cluster,
        task=task_arn
    )
    
    print(f"Destroyed Fargate container with ARN: {task_arn}")
    return response

def check_task_status(ecs_client, cluster, task):
    ecs_client = boto3.client('ecs')
    response = ecs_client.describe_tasks(
        cluster=cluster,
        tasks=[task]
    )
    
    for task in response['tasks']:
        print(f"Task {task['taskArn']} is {task['lastStatus']}")

    return response

######################################################################
#                       Lambda Handler                               #
######################################################################
def lambda_handler(event, context):
    try:
        # Extract request body
        command = json.loads(event["body"]).get("command")
        task_arn = json.loads(event["body"]).get("task_arn")

        # ECS Fargate Config
        ecs_client = boto3.client("ecs")
        task_definition = "minecraft-task-definition"
        cluster = "minecraft_cluster"
        subnet_id = os.getenv('DEFAULT_SUBNET_ID')
        security_group_id = os.getenv('DEFAULT_SECURITY_GROUP_ID')
        network_configuration = {
            "awsvpcConfiguration": {
                "subnets": [ subnet_id ],  # replace with your subnet
                "securityGroups": [ security_group_id],  # replace with your security group
                "assignPublicIp": "ENABLED"
            }
        }
        environment_variables = [
            { 
                "BOT_COMMAND": f"{command}", 
                "value2": "my_value2" 
            }, 
        ]
        
        if ( command != "status"):
            response = create_fargate_container(ecs_client, task_definition, cluster, network_configuration, environment_variables)
        else:
            # Check if task_arn is not null
            if not task_arn:
                print("Error: task_arn must not be null when checking task status")
                return {
                    'statusCode': 400,
                    'body': json.dumps('Error: task_arn must not be null when checking task status')
                }
            
            response =  check_task_status(ecs_client, cluster, task_arn)

    except (BotoCoreError, ClientError) as error:
        # If there was an error, return an HTTP 500 response with the error message
        print(f"Error running Fargate task: {error}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error running Fargate task: {error}")
        }

    return {
        "statusCode": 200,
        "body": json.dumps(response)
    }