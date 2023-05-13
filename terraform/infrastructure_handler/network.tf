########################
#    VPC and Subnets   #
########################
# Fetch the default VPC
data "aws_vpc" "default" {
  default = true
}

# Fetch the default Subnets of the default VPC
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [local.vpc_id]
  }
}

# Fetch the default Security Group of the default VPC
data "aws_security_group" "default" {
  vpc_id = data.aws_vpc.default.id
  name   = "default"
}


locals {
  vpc_id    = length(var.vpc_id) > 0 ? var.vpc_id : data.aws_vpc.default.id
  subnet_id = length(var.subnet_id) > 0 ? var.subnet_id : sort(data.aws_subnets.default.ids)[0]
  security_group_id = data.aws_security_group.default.id
}


