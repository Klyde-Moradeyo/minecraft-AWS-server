########################
#         Tags         #
########################

variable "label_id" {
  description = "ID from labels module"
  type        = string
}

variable "label_tags" {
  description = "Tags from labels module"
  type        = map(string)
}

########################
#    Lambda Function   #
########################
variable "lambda_runtime" {
  description = "Tags from labels module"
  type        = string
}

variable "lambda_timeout" {
  description = "Tags from labels module"
  type        = string
}

########################
#    Systems Manager   #
########################
variable "bot_command_name" {
  description = "SSM Store Containing the Command Fargate should run"
  type        = string
}

variable "terraform_token_name" {
  description = "Terraform token name in Systems Manager Parameter Store"
  type        = string
  default     = "terraform-cloud-user-api"
}

variable "discord_token_name" {
  description = "Discord token name in Systems Manager Parameter Store"
  type        = string
  default     = "discord-mango-machine-bot"
}

########################
#         ECS          #
########################
variable "ecs_cluster_name" {
  description = "ECS Cluster Name of the environment"
  type        = string
}

variable "ecs_container_name" {
  description = "ECS Container Name"
  type        = string
}

variable "ecs_task_definition_family" {
  description = "ECS Task Defintion Family"
  type        = string
}

########################
#        VPC           #
########################
variable "security_group_id" {
  description = "Security group ID"
  type        = string
}

variable "subnet_id" {
  description = "VPC subnet id to place the instance"
  type        = string
}

########################
#     Minecraft        #
########################
variable "mc_server_ip" {
  description = "Minecraft Server Host Name / IP"
  type        = string
}

variable "mc_port" {
  description = "TCP port for minecraft"
  type        = number
  default     = 25565
}







