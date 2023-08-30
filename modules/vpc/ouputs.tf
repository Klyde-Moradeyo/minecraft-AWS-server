output "vpc_id" {
  description = "The ID of the selected VPC."
  value       = local.vpc_id
}

output "subnet_id" {
  description = "The ID of the selected subnet."
  value       = local.subnet_id
}

output "security_group_id" {
  description = "The ID of the security group of the selected VPC."
  value       = local.security_group_id
}
