########################
#         IAM          #
########################
data "aws_iam_policy_document" "assume_role_lambda" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = [ "lambda.amazonaws.com" ]
    }

    actions = [ "sts:AssumeRole" ]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role_lambda.json
}

# Attach the SSM access policy to the Lambda IAM role
resource "aws_iam_role_policy_attachment" "ssm_access" {
  policy_arn = aws_iam_policy.ssm_access.arn
  role       = aws_iam_role.iam_for_lambda.name
}

# IAM policy to allow Lambda to access specific 
# SSM Parameter Store parameters
resource "aws_iam_policy" "ssm_access" {
  name        = "ssm_access"
  description = "IAM policy to allow Lambda access to specific SSM Parameter Store parameters"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # {
      #   Action   = [
      #     "ssm:GetParameter",
      #   ]
      #   Effect   = "Allow"
      #   Resource = [
      #     "arn:aws:ssm:*:847399026905:parameter/${var.git_private_key_name}",
      #     "arn:aws:ssm:*:847399026905:parameter/${var.terraform_token_name}",
      #     # "arn:aws:ssm:*:847399026905:parameter/mc_server/BOT_COMMAND",
      #   ]
      # },
      {
        Action   = [
          "ssm:PutParameter",
          "ssm:GetParameter"
        ]
        Effect   = "Allow"
        Resource = [
          "arn:aws:ssm:*:847399026905:parameter/mc_server/BOT_COMMAND",
        ]
      }
    ]
  })
}

# IAM policy for CloudWatch Logs
data "aws_iam_policy_document" "cloudwatch_logs" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }
}

# IAM policy to allow Lambda to access CloudWatch Logs
resource "aws_iam_policy" "lambda_cloudwatch_logs" {
  name        = "lambda_cloudwatch_logs"
  description = "IAM policy to allow Lambda to write to CloudWatch Logs"

  policy = data.aws_iam_policy_document.cloudwatch_logs.json
}

# lambda log group
resource "aws_cloudwatch_log_group" "example" {
  name              = "/aws/lambda/${aws_lambda_function.lambda_function.function_name}"
  retention_in_days = 1
}


# Attach the CloudWatch Logs access policy to the Lambda IAM role
resource "aws_iam_role_policy_attachment" "cloudwatch_logs" {
  policy_arn = aws_iam_policy.lambda_cloudwatch_logs.arn
  role       = aws_iam_role.iam_for_lambda.name
}

# Fargate Access 
data "aws_iam_policy_document" "fargate_access" {
  statement {
    effect = "Allow"

    actions = [
      "ecs:RunTask",
      "ecs:StopTask",
      "ecs:DescribeTasks",
      "ecs:ListTasks",
      "iam:PassRole",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy" "lambda_fargate_access" {
  name        = "lambda_fargate_access"
  description = "IAM policy to allow Lambda to manage Fargate tasks"

  policy = data.aws_iam_policy_document.fargate_access.json
}

resource "aws_iam_role_policy_attachment" "fargate_access" {
  policy_arn = aws_iam_policy.lambda_fargate_access.arn
  role       = aws_iam_role.iam_for_lambda.name
}

########################
#    Lambda Function   #
########################
resource "aws_lambda_function" "lambda_function" {
  depends_on = [ aws_ecs_cluster.my_cluster ]

  filename            = "./lambda_function_payload.zip"
  source_code_hash    = filebase64sha256("./lambda_function_payload.zip") # Check the zip file SHA256 to for any changes
  function_name       = "${var.name}-lambda-function"
  role                = aws_iam_role.iam_for_lambda.arn
  handler             = "lambda_function.lambda_handler"
  runtime             = "python3.8"
  timeout             = 900  # Set the timeout to the max (15 minutes)

  # layers = [ 
  #   local.git_lambda_layer_arn,
  #   aws_lambda_layer_version.terraform_lambda_layer.arn
  #   ]

  environment {
    variables = {
      DISCORD_TOKEN = var.discord_token_name
      DEFAULT_SUBNET_ID = local.subnet_id
      DEFAULT_SECURITY_GROUP_ID = local.security_group_id
      CONTAINER_NAME = var.ecr_repo_name
      TF_USER_TOKEN = var.terraform_token_name
      CLUSTER = aws_ecs_cluster.my_cluster.name

      # Tags
      TAG_NAME = "${var.environment}-${var.name}"
      TAG_NAMESPACE = var.namespace
      TAG_ENVIRONMENT = var.environment
    }
  }

  tags = module.label.tags
}

########################
#     Lambda Layer     #
########################
# locals {
#   git_lambda_layer_arn = "arn:aws:lambda:${var.aws_region}:553035198032:layer:git-lambda2:8"
# }

# resource "aws_lambda_layer_version" "terraform_lambda_layer" {
#   filename   = "${path.module}/../../lambda/terraform_layer.zip"  # Replace with your layer ZIP filename
#   layer_name = "terraform_lambda_layer"
#   compatible_runtimes = [ "python3.8" ]  # Replace with your desired runtime
# }

