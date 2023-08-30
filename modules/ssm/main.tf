resource "aws_ssm_parameter" "mc_server_private_key" {
  name  = "/${var.label_id}/${var.parameter_name}"
  type  = var.parameter_type
  value = var.value != "NOT_SET" ? var.value : "null"
  key_id = "alias/aws/ssm" # Default key for Parameter Store
}