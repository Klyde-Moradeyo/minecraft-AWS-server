
########################
#     General AWS      #
########################
# output "aws_account_id" {
#   description = "The AWS Account ID"
#   value       = data.aws_caller_identity.aws.account_id
# }

########################
#         EIP          #
########################
output "eip" {
  value = module.eip.eip_public_ip
}

########################
#         VPC          #
########################
output "vpc_id" {
  description = "The VPC ID"
  value       = module.vpc.vpc_id
}

output "subnet_id" {
  description = "The Subnet ID"
  value       = module.vpc.subnet_id
}

output "security_group_id" {
  description = "The Subnet ID"
  value       = module.vpc.security_group_id
}

########################
#       S3 Bucket      #
########################
output "mc_s3_bucket_name" {
  description = "The name of the Minecraft S3 bucket"
  value       = module.s3_mc_world.s3_bucket_name
}

output "mc_s3_bucket_arn" {
  description = "The ARN of the Minecraft S3 bucket"
  value       = module.s3_mc_world.s3_bucket_arn
}

output "mc_s3_bucket_uri" {
  description = "The S3 uri of the minecraft world data"
  value       = module.s3_mc_world.s3_bucket_uri
}

# output "mc_archive_s3_bucket_uri" {
#   description = "The name of the S3 bucket for logs"
#   value       = "WIP --- s3://${aws_s3_bucket.mc_s3.id}"
# }

# output "mc_archive_s3_bucket_arn" {
#   description = "The S3 uri of the minecraft world data"
#   value       = "module.s3_mc_world.s3_bucket_uri"
# }

########################
#     API Gateway      #
########################
output "api_gateway_url" {
  value = module.api_gateway.api_gateway_url
}

########################
#         EC2          #
########################
output "ec2_key_pair" {
  value = module.ec2_key_pair.key_pair_name
}

output "ec2_private_key" {
  description = "The private key part of the key pair"
  value       = module.ec2_key_pair.private_key_pem
  sensitive   = true
}

########################
#         ECR          #
########################
output "ecr_repository_name" {
  value = module.ecs_cluster.ecr_repository_name
}

########################
#         ECS          #
########################
output "ecs_cluster_name" {
  description = "The name of the ECS cluster"
  value       = module.ecs_cluster.ecs_cluster_name
}

output "ecs_container_name" {
  description = "The name of the container in the ECS task definition"
  value       = module.ecs_cluster.ecs_task_definition_container_name
}

output "ecs_container_image" {
  description = "The image URL of the container in the ECS task definition"
  value       = module.ecs_cluster.ecs_task_definition_container_image
}

########################
#         Tags         #
########################
output "label_id" {
  description = "Label ID"
  value     = module.labels.label_id
}

output "label_tags" {
  description = "Label tags"
  value     = module.labels.label_tags
}