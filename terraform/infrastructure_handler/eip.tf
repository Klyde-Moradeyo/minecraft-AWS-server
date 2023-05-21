data "aws_caller_identity" "aws" {}

########################
#       Labels         #
########################
module "label" {
  source   = "cloudposse/label/null"
  version = "0.25.0"

  namespace   = var.namespace
  stage       = var.environment
  name        = var.name
  delimiter   = "-"
  label_order = ["environment", "stage", "name", "attributes"]
  tags        = merge(var.tags, local.tf_tags)
}

locals {
  tf_tags = {
    Terraform = true,
    By        = data.aws_caller_identity.aws.arn
  }
}

########################
#         EIP          #
########################
resource "aws_eip" "mc_server_eip" {
  vpc = true

  tags = module.label.tags
}

# resource "null_resource" "EIP_to_txt_file" {
#   depends_on = [ aws_eip.mc_server_eip ]

#   provisioner "local-exec" {
#     command = "echo '${aws_eip.mc_server_eip.public_ip}' > EIP.txt"
#   }
# }

# resource "null_resource" "delete_EIP_to_txt_file" {
#   depends_on = [ aws_eip.mc_server_eip ]

#   triggers = {
#     before_destroy_timestamp = timestamp()
#   }

#   provisioner "local-exec" {
#     when    = destroy # Only execute on destruction of resource
#     command = "rm -f EIP.txt"
#   }
# }


