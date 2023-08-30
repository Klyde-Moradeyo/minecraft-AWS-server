########################
#       S3 Bucket      #
########################
locals {
  s3_bucket_name = "${var.label_id}-${var.bucket_name}"
}

resource "aws_s3_bucket" "mc_s3" {
  bucket = local.s3_bucket_name

  force_destroy = var.bucket_force_destroy

  tags = var.label_tags
}

resource "aws_s3_bucket_public_access_block" "mc_s3_public_access_block" {
  bucket = aws_s3_bucket.mc_s3.id

  # S3 bucket-level Public Access Block configuration
  # block_public_acls       = true # blocks the creation or modification of any new public ACLs on the bucket
  # block_public_policy     = true # blocks the creation or modification of any new public bucket policies
  # ignore_public_acls      = true # instructs Amazon S3 to ignore all public ACLs associated with the bucket and its objects
  # restrict_public_buckets = true # restricts access to the bucket and its objects to only AWS services and authorized users
}

resource "aws_s3_bucket_versioning" "mc_s3" {
  bucket = local.s3_bucket_name

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