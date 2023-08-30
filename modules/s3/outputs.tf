########################
#       S3 Bucket      #
########################
output "s3_bucket_name" {
  description = "The name of the Minecraft S3 bucket"
  value       = aws_s3_bucket.mc_s3.id
}

output "s3_bucket_arn" {
  description = "The ARN of the Minecraft S3 bucket"
  value       = aws_s3_bucket.mc_s3.arn
}

output "s3_bucket_uri" {
  description = "The ARN of the S3 bucket for logs"
  value       = "s3://${aws_s3_bucket.mc_s3.id}"
}