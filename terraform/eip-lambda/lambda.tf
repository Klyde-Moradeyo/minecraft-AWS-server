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
      {
        Action   = [
          "ssm:GetParameter",
        ]
        Effect   = "Allow"
        Resource = [
          "arn:aws:ssm:*:847399026905:parameter/${var.git_private_key_name}",
          "arn:aws:ssm:*:847399026905:parameter/${var.discord_token_name}",
        ]
      }
    ]
  })
}

########################
#    Lambda Function   #
########################
resource "aws_lambda_function" "lambda_function" {
  filename            = "${path.module}/../../lambda/lambda_function_payload.zip"
  function_name       = "${var.name}-lambda-function"
  role                = aws_iam_role.iam_for_lambda.arn
  handler             = "lambda_function.lambda_handler"
  runtime             = "python3.8"
  timeout             = 900  # Set the timeout to the max (15 minutes)

  layers = [ 
    local.git_lambda_layer_arn,
    aws_lambda_layer_version.terraform_lambda_layer.arn
    ]

  depends_on = [
    aws_iam_role_policy_attachment.ssm_access,
  ]

  environment {
    variables = {
      DISCORD_TOKEN = var.discord_token_name
      # PATH = "/var/task/bin:/usr/local/bin:/usr/bin/:/bin:/opt/bin"
    }
  }

  tags = module.label.tags
}

########################
#     Lambda Layer     #
########################
locals {
  git_lambda_layer_arn = "arn:aws:lambda:${var.aws_region}:553035198032:layer:git-lambda2:8"
}

resource "aws_lambda_layer_version" "terraform_lambda_layer" {
  filename   = "${path.module}/../../lambda/terraform_layer.zip"  # Replace with your layer ZIP filename
  layer_name = "terraform_lambda_layer"
  compatible_runtimes = [ "python3.8" ]  # Replace with your desired runtime
}

