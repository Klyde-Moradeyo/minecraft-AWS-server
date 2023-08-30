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
#        Lambda        #
########################
variable "lambda_function_name" {
  description = "Target Lambda function name"
  type        = string
}

variable "lambda_invoke_arn" {
  description = "The Invoke ARN of the Target Lambda function"
  type        = string
}






