data "aws_vpc" "default" {
  default = true
}

data "aws_subnet_ids" "default" {
  vpc_id = local.vpc_id
}

locals {
  vpc_id    = length(var.vpc_id) > 0 ? var.vpc_id : data.aws_vpc.default.id
  subnet_id = length(var.subnet_id) > 0 ? var.subnet_id : sort(data.aws_subnet_ids.default.ids)[0]
}
