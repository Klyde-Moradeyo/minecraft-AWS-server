data "aws_caller_identity" "aws" {}

locals {
  tf_tags = {
    Terraform = true,
    By        = data.aws_caller_identity.aws.arn
  }
}

########################
#    IAM Role for      #
#   Ec2 to S3 acces    #
########################
resource "aws_iam_role" "allow_s3" {
  name   = "${module.label.id}-allow-ec2-to-s3"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

# Used to pass the role information to an EC2 instance
resource "aws_iam_instance_profile" "mc" {
  name = "${module.label.id}-instance-profile"
  role = aws_iam_role.allow_s3.name
}

# The policy grants permissions to list the specified S3 bucket and 
# to perform put, get, and delete actions on objects within the bucket.
resource "aws_iam_role_policy" "mc_allow_ec2_to_s3" {
  name   = "${module.label.id}-allow-ec2-to-s3"
  role   = aws_iam_role.allow_s3.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": ["arn:aws:s3:::${local.bucket_name}"]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": ["arn:aws:s3:::${local.bucket_name}/*"]
    }
  ]
}
EOF
}