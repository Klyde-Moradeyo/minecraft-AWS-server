########################
#        VPC           #
########################
variable "vpc_id" {
  description = "VPC for security group"
  type        = string
  default     = ""
}

variable "subnet_id" {
  description = "VPC subnet id to place the instance"
  type        = string
  default     = ""
}