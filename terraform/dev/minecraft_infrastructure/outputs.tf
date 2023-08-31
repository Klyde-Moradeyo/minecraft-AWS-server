output ami_id {
    value = module.minecraft_server.ami_id
}

output "id" {
  value = module.minecraft_server.id
}

output "public_ip" {
  value = module.minecraft_server.public_ip
}

output "vpc_id" {
  value = module.minecraft_server.vpc_id
}

output "subnet_id" {
  value = module.minecraft_server.subnet_id
}

output "minecraft_server" {
  value = module.minecraft_server.minecraft_server
}

########################
#         Tags         #
########################
output "label_id" {
  description = "Label ID"
  value     = local.label_id
}

output "label_tags" {
  description = "Label tags"
  value     = local.label_tags
}