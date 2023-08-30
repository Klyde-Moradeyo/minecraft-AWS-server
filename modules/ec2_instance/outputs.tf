output ami_id {
    value = data.aws_ami.ubuntu.id
}

output "id" {
  value = module.ec2_instance.id
}

output "public_ip" {
  value = module.ec2_instance.public_ip
}

output "vpc_id" {
  value = var.vpc_id
}

output "subnet_id" {
  value = var.subnet_id
}

output "minecraft_server" {
  value = "${module.ec2_instance.public_ip}:${var.mc_port}"
}