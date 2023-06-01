# Terraform Block
terraform {
  required_version = "~> 1.4" # which means any version equal & above 0.14 like 0.15, 0.16 etc and < 1.xx
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }

  cloud {
    organization = "mango-dev"

    workspaces {
      name = "minecraft-infra-handler"
    }
  }
}

# Provider Block
provider "aws" {
  region  = var.aws_region
}

data "aws_caller_identity" "aws" {}

locals {
  user_name = split("/", data.aws_caller_identity.aws.arn)[2]
}
