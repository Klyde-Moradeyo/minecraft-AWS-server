########################
#         EIP          #
########################
output "eip" {
  value = aws_eip.mc_server_eip.public_ip
}

output "eip_allocation_id" {
  description = "The EIP Allocation ID for the Minecraft server"
  value       = aws_eip.mc_server_eip.id
}

output "eip_public_ip" {
  description = "The EIP Public IP of the Minecraft server"
  value       = aws_eip.mc_server_eip.public_ip
}