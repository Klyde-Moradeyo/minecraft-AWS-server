import boto3
import time
import json
from botocore.exceptions import BotoCoreError, ClientError
from utils.event_parser import APIEventParser
from utils.env_manager import EnvironmentVariables
from utils.minecraft import MinecraftServerChecker
from utils.fargate import Fargate
from utils.time_utils import seconds_to_minutes, DateTimeEncoder
from utils.ssm import SSMUtil
from utils.logger import setup_logging

class LambdaHandler:
    def __init__(self, event):
        # Setting up logging
        self.logger = setup_logging() 
        
        # Parse the event
        event_parser = APIEventParser(event)
        event_body = event_parser.parse()
        self.logger.info(f"Event Body: \n{event_body}")

        # Extract the action from the parsed event
        self.ACTION = event_body["command"]

        # Get the environment variables specific to the action
        envs = EnvironmentVariables(self.ACTION).get_vars()  # Get Environment Variables

        # Initialize Fargate class
        self.tec_fargate = Fargate(envs['CLUSTER'])  # TEC means Terraform Execution Container
        self.task_tags = self.tec_fargate.get_task_tags()

        # Initialize SSM class
        self.ssm = SSMUtil()

        # Perform checks
        self.mc_server_status = MinecraftServerChecker.check_mc_server(envs["MC_SERVER_IP"], envs["MC_PORT"])  # Check If minecraft server is online/offline
        self.is_task_running = self.tec_fargate.is_task_with_tags_exists(self.task_tags)  # Check if there's a Fargate task running
    
    def execute_command(self):
        try:
            if self.command == "mc_world_archive":
                response = self.handle_mc_world_archive()
            elif self.command in ('start', 'stop'):
                response = self.handle_start_stop(self.command)
            elif self.command == 'status':
                response = self.handle_status()
            else:
                raise ValueError(f"Invalid command: {self.command}")
            
            return {
                "statusCode": 200,
                "body": json.dumps(response, cls=DateTimeEncoder)
            }
        except ValueError as error:
            self.logger.error("Value error occurred", extra={"error": str(error)})
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(error)}, cls=DateTimeEncoder)
            }
        except (BotoCoreError, ClientError) as error:
            self.logger.exception("Boto3 related error occurred", extra={"error": str(error)})
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(error)}, cls=DateTimeEncoder)
            }
        except Exception as error:
            self.logger.exception("Unhandled exception occurred", extra={"error": str(error)})
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(error)}, cls=DateTimeEncoder)
            }
        
    def launch_new_fargate_task(self):
        """
        Launch a new Fargate task and return its status.
        """
        self.ssm.send_param(self.ACTION, "String", self.envs["BOT_COMMAND_NAME"])

        # Launch Fargate Container
        task_arn = self.tec_fargate.create_fargate_container()
        self.logger.info(f"New Fargate task launched: {task_arn}")

        # Confirm the task i running
        task_status = self.tec_fargate.check_task_status(self.task_tags)
        if task_status is None:
            raise Exception(f"Error running Starting Task: {task_arn}")
        
        return task_arn, task_status
        
    def handle_start(self):
        if self.mc_server_status["online"]:
            return {"STATUS": "MC_SERVER_ALREADY_UP"}
        
        task_arn, task_status = self.launch_new_fargate_task()

        if self.is_task_running:
            prev_command = self.ssm.get_param(self.envs["BOT_COMMAND_NAME"])

        return {"STATUS": task_status, "PREVIOUS_COMMAND": prev_command}

    def handle_stop(self):
        if not self.mc_server_status["online"]:
            return {"STATUS": "MC_SERVER_ALREADY_DOWN"}

        task_arn, task_status = self.launch_new_fargate_task()
        if self.is_task_running:
            prev_command = self.ssm.get_param(self.envs["BOT_COMMAND_NAME"])

        return {"STATUS": task_status, "PREVIOUS_COMMAND": prev_command}

    def handle_status(self):
        if self.is_task_running:
            task_status = self.tec_fargate.check_task_status(self.task_tags)
        else:
            if self.mc_server_status["online"]:
                task_status = "MC_SERVER_UP"
            else:
                task_status = "MC_SERVER_DOWN"

        prev_command = self.ssm.get_param(self.envs["BOT_COMMAND_NAME"])
        return {'STATUS': task_status, 'PREVIOUS_COMMAND': prev_command}

    def handle_mc_world_archive(self):
        """
        Handle Minecraft world archive tasks. Wait for any running task to finish, then launch a new Fargate task.
        """
        # If a task is currently running, wait for it to finish up to a time limit
        if self.is_task_running:
            check_interval = 60
            time_limit = 600
            start_time = time.time()
            self.logger.info(f"waiting for {seconds_to_minutes(time_limit)} minutes")

            while (time.time() - start_time) < time_limit:
                self.is_task_running = self.tec_fargate.is_task_with_tags_exists(self.task_tags)
                if not self.is_task_running:
                    task_arn, task_status = self.launch_new_fargate_task()
                    return { "STATUS": f"MC_WORLD_ARCHIVE", "INFO": f"New Fargate task launched: {task_arn} | {task_status}" }

                time.sleep(check_interval)
                elapsed = time.time() - start_time
                self.logger.info(f"time elapsed: {int(elapsed)} seconds")

            self.logger.warning(f"Fargate task still running after {seconds_to_minutes(elapsed)} minutes.")
            return { "STATUS": f"MC_WORLD_ARCHIVE_FAILED_START", "INFO": f"Timed out" }
        
        # If no task is running, directly launch a new one
        self.launch_new_fargate_task()
        return { "STATUS": f"MC_WORLD_ARCHIVE", "INFO": f"New Fargate task launched: {task_arn} | {task_status}" } # Surely I should be used previous command here instead

# Where the magic happens
def lambda_handler(event, context):
    handler = LambdaHandler(event)
    return handler.execute_command()
