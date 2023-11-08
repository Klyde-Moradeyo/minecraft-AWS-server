########################
#         Tags         #
########################
variable "label_id" {
  description = "ID from labels module"
  type        = string
}

variable "label_tags" {
  description = "Tags from labels module"
  type        = map(string)
}

########################
#       S3 Bucket      #
########################
variable "bucket_name" {
  description = "Bucket Name"
  type        = string
}

variable "bucket_force_destroy" {
  description = "Boolean that indicates all objects should be deleted from the bucket"
  type        = bool
  default     = false
}

variable "version_config_status" {
  description = "Boolean that indicates all objects should be deleted from the bucket"
  type        = string
  default     = "Disabled"
}