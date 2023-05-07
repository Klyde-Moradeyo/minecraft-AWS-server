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
          "ssm:GetParameters",
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
data "archive_file" "lambda" {
  type        = "zip"
  source_file = "${path.module}/../../lambda/lambda_function_payload.zip"
  output_path = "lambda_function_payload.zip"
}

resource "aws_lambda_function" "lambda_function" {
  filename            = "lambda_function_payload.zip"
  function_name       = "mc-server-lambda"
  role                = aws_iam_role.iam_for_lambda.arn
  source_code_hash    = data.archive_file.lambda.output_base64sha256
  handler             = "lambda_function.lambda_handler"
  runtime             = "python3.8"

  depends_on = [
    aws_iam_role_policy_attachment.ssm_access,
  ]

  environment {
    variables = {
      DISCORD_TOKEN = var.discord_token_name
    }
  }

  tags = module.label.tags
}

