
########################
#     General AWS      #
########################
variable "aws_region" {
  description = "Region in which AWS Resources to be created"
  type = string
  default = "eu-west-2"
}

########################
#    Lambda Function   #
########################
variable "lambda_runtime" {
  description = "Tags from labels module"
  type        = string
  default     = "python3.10" 
}

variable "lambda_timeout" {
  description = "Timeout for Lambda execution"
  type        = number
  default     = 900   # Set the timeout to the max (15 minutes)
}

########################
#     Minecraft        #
########################
variable "mc_port" {
  description = "TCP port for minecraft"
  type        = number
  default     = 25565
}

# variable "mc_backup_freq" {
#   description = "How often (mins) to sync to S3"
#   type        = number
#   default     = 5
# }

########################
#    Systems Manager   #
########################
variable "bot_command_name" {
  description = "SSM Store Containing the Command Fargate should run"
  type        = string
  default     = "mc_server/BOT_COMMAND"
}

variable "terraform_token_name" {
  description = "Terraform token name in Systems Manager Parameter Store"
  type        = string
  default     = "terraform-cloud-user-api"
}

variable "git_private_key_name" {
  description = "Private Key name for Github SSH in Systems Manager Parameter Store"
  type        = string
  default     = "dark-mango-bot-private-key"
}





