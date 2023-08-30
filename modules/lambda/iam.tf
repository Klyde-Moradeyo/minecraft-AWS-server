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
  name               = "${var.label_id}-iam-for-lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role_lambda.json
}

########################
#         SSM          #
########################
# Attach the SSM access policy to the Lambda IAM role
resource "aws_iam_role_policy_attachment" "ssm_access" {
  policy_arn = aws_iam_policy.ssm_access.arn
  role       = aws_iam_role.iam_for_lambda.name
}

# IAM policy to allow Lambda to access specific 
# SSM Parameter Store parameters
resource "aws_iam_policy" "ssm_access" {
  name        = "${var.label_id}-ssm-access"
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
          "arn:aws:ssm:*:847399026905:parameter/${var.bot_command_name}",
        ]
      }
    ]
  })
}

########################
#        Fargate       #
########################
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
  name        = "${var.label_id}-lambda-fargate-access"
  description = "IAM policy to allow Lambda to manage Fargate tasks"

  policy = data.aws_iam_policy_document.fargate_access.json
}

resource "aws_iam_role_policy_attachment" "fargate_access" {
  policy_arn = aws_iam_policy.lambda_fargate_access.arn
  role       = aws_iam_role.iam_for_lambda.name
}


########################
#      Cloud Watch     #
########################
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
  name        = "${var.label_id}-lambda-cloudwatch-logs"
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