########################
#   Security Groups    #
########################
resource "aws_security_group" "minecraft_SG" {
  name        = "${var.label_id}-sg"
  description = "Minecraft Security Group Allow SSH and TCP"
  vpc_id      = var.vpc_id // default VPC

  # Ingress rule for SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    description = "SSH"
    cidr_blocks = [ var.allowed_cidrs ]
  }

  # Ingress rule for Minecraft server
  ingress {
    description      = "Minecraft Server"
    from_port        = var.mc_port
    to_port          = var.mc_port
    protocol         = "tcp"
    cidr_blocks      = [ var.allowed_cidrs ]
  }

  // Allow all outgoing traffic without any restrictions
  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = var.label_tags
}