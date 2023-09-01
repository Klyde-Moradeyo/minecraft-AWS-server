########################
#       Labels         #
########################
module "labels" {
  # source = "../modules/ec2_instance"
  source = "github.com/Klyde-Moradeyo/minecraft-AWS-server//modules/labels?ref=tf-infra-service-modules"

  environment = "dev"
}

########################
#        VPC           #
########################
module "vpc" {
  source = "github.com/Klyde-Moradeyo/minecraft-AWS-server//modules/vpc?ref=tf-infra-service-modules"
}


########################
#         EIP          #
########################
module "eip" {
  source = "github.com/Klyde-Moradeyo/minecraft-AWS-server//modules/eip?ref=tf-infra-service-modules"

  # Module labels
  label_id                         = module.labels.label_id
  label_tags                       = module.labels.label_tags
}

########################
#     EC2 Key Pair     #
########################
module "ec2_key_pair" {
  source = "terraform-aws-modules/key-pair/aws"
  version = "2.0.2"

  key_name   = "${module.labels.label_id}-key"
  create_private_key = true
}

########################
#    Systems Manager   #
########################
module "ssm_mc_server_private_key" {
  source = "github.com/Klyde-Moradeyo/minecraft-AWS-server//modules/ssm?ref=tf-infra-service-modules"

  parameter_name = "mc_server/private_key"
  parameter_type = "SecureString"
  value          = module.ec2_key_pair.private_key_pem

  # Module labels
  label_id                         = module.labels.label_id
  label_tags                       = module.labels.label_tags
}

module "ssm_bot_command" {
  source = "github.com/Klyde-Moradeyo/minecraft-AWS-server//modules/ssm?ref=tf-infra-service-modules"

  parameter_name = var.bot_command_name
  parameter_type = "String"

  # Module labels
  label_id                         = module.labels.label_id
  label_tags                       = module.labels.label_tags
}

########################
#         ECS          #
########################
module "ecs_cluster" {
  source = "github.com/Klyde-Moradeyo/minecraft-AWS-server//modules/ecs?ref=tf-infra-service-modules"

  # ECS
  ecr_repo_name = "mc-infra-runner"
  ecs_cpu_limit = "256"
  ecs_memory_limit = "1024"
  aws_region = var.aws_region

  # SSM
  git_private_key_name = "dark-mango-bot-private-key"
  ec2_private_key_name = module.ssm_mc_server_private_key.ssm_parameter_name
  bot_command_name = module.ssm_bot_command.ssm_parameter_name
  terraform_token_name = "terraform-cloud-user-api"

  # IAM
  s3_bucket_arns = module.s3_mc_world.s3_bucket_arn

  # Module labels
  label_id                         = module.labels.label_id
  label_tags                       = module.labels.label_tags
}

########################
#     API Gateway      #
########################
module "api_gateway" {
  source = "github.com/Klyde-Moradeyo/minecraft-AWS-server//modules/api_gateway?ref=tf-infra-service-modules"

  # lambda integration
  lambda_function_name = module.lambda.lambda_function_name
  lambda_invoke_arn = module.lambda.lambda_function_invoke_arn

  # Module labels
  label_id                         = module.labels.label_id
  label_tags                       = module.labels.label_tags
}

########################
#    Lambda Function   #
########################
module "lambda" {
  source = "github.com/Klyde-Moradeyo/minecraft-AWS-server//modules/lambda?ref=tf-infra-service-modules"
  depends_on = [ module.ecs_cluster ]

  # Lambda Config
  lambda_runtime = var.lambda_runtime
  lambda_timeout = var.lambda_timeout

  # SSM
  bot_command_name = module.ssm_bot_command.ssm_parameter_name
  terraform_token_name = var.terraform_token_name
  discord_token_name = var.discord_token_name

  # Lambda Environment vars
  ecs_cluster_name = module.ecs_cluster.ecs_cluster_name
  ecs_container_name = module.ecs_cluster.ecs_task_definition_container_name
  subnet_id = module.vpc.subnet_id
  security_group_id = module.vpc.security_group_id
  mc_server_ip = module.eip.eip_public_ip
  mc_port =  var.mc_port
  ecs_task_definition_family = module.ecs_cluster.ecs_task_definition_family

  # Module labels
  label_id                         = module.labels.label_id
  label_tags                       = module.labels.label_tags
}

########################
#       S3 Bucket      #
########################
resource "random_string" "unique_bucket_suffix" {
  length  = 8
  special = false
  upper   = false
  numeric  = false
}

module "s3_mc_world" {
  source = "github.com/Klyde-Moradeyo/minecraft-AWS-server//modules/s3?ref=tf-infra-service-modules"
  
  # S3 Bucket 
  bucket_name = "s3-${random_string.unique_bucket_suffix.result}"

  # Module labels
  label_id                         = module.labels.label_id
  label_tags                       = module.labels.label_tags
}
