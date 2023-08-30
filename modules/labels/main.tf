########################
#       Labels         #
########################
// Fetch the details of the current AWS account 
// and user or role that Terraform is using to make API calls.
data "aws_caller_identity" "aws" {}

locals {
  user_name = split("/", data.aws_caller_identity.aws.arn)[1]
  tf_tags = {
    Terraform = true,
    By        = data.aws_caller_identity.aws.arn
  }
}

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