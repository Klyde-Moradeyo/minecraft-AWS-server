########################
#         EIP          #
########################
resource "aws_eip" "mc_server_eip" {
  vpc = true

  tags = var.label_tags
}


