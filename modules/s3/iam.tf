#############################
# Give Current User Access  #
#############################
data "aws_caller_identity" "aws" {}

locals {
  user_name = split("/", data.aws_caller_identity.aws.arn)[2]
}

resource "aws_iam_policy" "s3_bucket_access" {
  name        = "${var.label_id}-S3BucketAccess"
  path        = "/"
  description = "IAM policy for providing S3 bucket access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${aws_s3_bucket.mc_s3.bucket}/*",
          "arn:aws:s3:::${aws_s3_bucket.mc_s3.bucket}"
        ]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "user_s3_access" {
  user       = local.user_name
  policy_arn = aws_iam_policy.s3_bucket_access.arn
}
