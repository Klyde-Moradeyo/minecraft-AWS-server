########################
#         ECR          #
########################
output "ecr_repository_url" {
  value = aws_ecr_repository.mc_repository.repository_url
}

output "ecr_repository_name" {
  value = aws_ecr_repository.mc_repository.name
}

########################
#         ECS          #
########################
output "ecs_cluster_name" {
  description = "The name of the ECS cluster"
  value       = aws_ecs_cluster.my_cluster.name
}

output "ecs_task_definition_family" {
  description = "The family of the ECS task definition"
  value       = aws_ecs_task_definition.my_task.family
}

output "ecs_task_definition_container_name" {
  description = "The name of the container in the ECS task definition"
  value       = jsondecode(aws_ecs_task_definition.my_task.container_definitions)[0].name
}

output "ecs_task_definition_container_image" {
  description = "The image URL of the container in the ECS task definition"
  value       = jsondecode(aws_ecs_task_definition.my_task.container_definitions)[0].image
}