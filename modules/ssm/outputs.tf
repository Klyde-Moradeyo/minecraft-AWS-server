output "ssm_parameter_name" {
  description = "The name of the SSM parameter for the Minecraft server private key"
  value       = replace(aws_ssm_parameter.mc_server_private_key.name, "^/", "")
}
