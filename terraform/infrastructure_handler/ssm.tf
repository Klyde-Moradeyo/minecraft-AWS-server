resource "aws_ssm_parameter" "mc_server_private_key" {
  name  = "/mc_server/private_key"
  type  = "SecureString"
  value = ""
  key_id = "alias/aws/ssm" # Default key for Parameter Store
}