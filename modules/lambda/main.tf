########################
#    Lambda Function   #
########################
resource "aws_lambda_function" "lambda_function" {

  filename            = "./lambda_function_payload.zip"
  source_code_hash    = filebase64sha256("./lambda_function_payload.zip") # Check the zip file SHA256 to for any changes
  function_name       = "${var.label_id}-lambda-function"
  role                = aws_iam_role.iam_for_lambda.arn
  handler             = "lambda_function.lambda_handler"
  runtime             = var.lambda_runtime
  timeout             = var.lambda_timeout

  environment {
    variables = {
      MC_SERVER_IP = var.mc_server_ip
      MC_PORT = var.mc_port
      GIT_PRIVATE_KEY = var.discord_token_name
      EC2_PRIVATE_KEY = var.ec2_private_key_name
      SUBNET_ID = var.subnet_id  # These vars need to be changed in lambda python
      SECURITY_GROUP_ID = var.security_group_id# These vars need to be changed in lambda python
      CONTAINER_NAME = var.ecs_container_name
      TF_USER_TOKEN = var.terraform_token_name
      CLUSTER = var.ecs_cluster_name
      BOT_COMMAND_NAME = var.bot_command_name
      TASK_DEFINITION_NAME = var.ecs_task_definition_family

      # Tags
      TAGS_JSON = jsonencode(var.label_tags)
      # Python Lambda function will need to be refactored to:
      # tags = json.loads(os.environ['TAGS_JSON'])
      # name = tags['Name']
      # namespace = tags['Namespace']
      # environment = tags['Stage']
    }
  }

  # layers = [ 
  #   local.git_lambda_layer_arn,
  #   aws_lambda_layer_version.terraform_lambda_layer.arn
  #   ]

  tags = var.label_tags
}

########################
#     Lambda Layer     #
########################
# locals {
#   git_lambda_layer_arn = "arn:aws:lambda:${var.aws_region}:553035198032:layer:git-lambda2:8"
# }

# resource "aws_lambda_layer_version" "terraform_lambda_layer" {
#   filename   = "${path.module}/../../lambda/terraform_layer.zip"  # Replace with your layer ZIP filename
#   layer_name = "terraform_lambda_layer"
#   compatible_runtimes = [ "python3.8" ]  # Replace with your desired runtime
# }

