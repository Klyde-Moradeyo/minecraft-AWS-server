########################
#       S3 Bucket      #
########################
resource "random_string" "unique_bucket_suffix" {
  length  = 8
  special = false
  upper   = false
  numeric  = false
}

locals {
  mc_bucket_name = "${var.name}-s3-${random_string.unique_bucket_suffix.result}"
  log_bucket_name = "${var.name}-log-s3-${random_string.unique_bucket_suffix.result}"
}

### Minecraft Server Bucket ###
resource "aws_s3_bucket" "mc_s3" {
  depends_on = [ aws_s3_bucket.log_bucket ]
  bucket = local.mc_bucket_name

  force_destroy = var.bucket_force_destroy

  tags = module.label.tags
}

resource "aws_s3_bucket_public_access_block" "mc_s3_public_access_block" {
  bucket = aws_s3_bucket.mc_s3.id

  # S3 bucket-level Public Access Block configuration
  block_public_acls       = true # blocks the creation or modification of any new public ACLs on the bucket
  block_public_policy     = true # blocks the creation or modification of any new public bucket policies
  ignore_public_acls      = true # instructs Amazon S3 to ignore all public ACLs associated with the bucket and its objects
  restrict_public_buckets = true # restricts access to the bucket and its objects to only AWS services and authorized users
}

resource "aws_s3_bucket_versioning" "mc_s3" {
  bucket = local.mc_bucket_name

  versioning_configuration {
    status    = "Suspended"
  }
}


resource "aws_s3_bucket_ownership_controls" "mc_s3_ownership_control" {
  bucket = aws_s3_bucket.mc_s3.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "mc_s3_acl" {
  depends_on = [aws_s3_bucket_ownership_controls.mc_s3_ownership_control]

  bucket = aws_s3_bucket.mc_s3.id
  acl    = "private"
}

########################
#     S3 LOG Bucket    #
########################
resource "aws_s3_bucket" "log_bucket" {
  bucket = local.log_bucket_name
}

resource "aws_s3_bucket_logging" "mc_s3_logging" {
  target_bucket = aws_s3_bucket.log_bucket.id
  target_prefix = "log/${local.mc_bucket_name}-logs"
  bucket        = aws_s3_bucket.mc_s3.id
}

data "aws_iam_policy_document" "s3_policy" {
  statement {
    actions = [
      "s3:GetObject",
      "s3:PutObject",
    ]

    resources = [
      "${aws_s3_bucket.log_bucket.arn}/*"
    ]
    principals {
      type        = "AWS"
      identifiers = [ data.aws_caller_identity.aws.arn ]
    }
  }
}

resource "aws_s3_bucket_policy" "log_bucket_policy" {
  bucket = aws_s3_bucket.log_bucket.id
  policy = data.aws_iam_policy_document.s3_policy.json
}