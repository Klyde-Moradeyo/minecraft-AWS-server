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

########################
#    Lambda Function   #
########################
data "archive_file" "lambda" {
  type        = "zip"
  source_file = "${path.module}/../../lambda/lambda_deployment.zip"
  output_path = "lambda_function_payload.zip"
}

resource "aws_lambda_function" "lambda_function" {
  filename            = "lambda_function_payload.zip"
  function_name       = "lambda_function_name"
  role                = aws_iam_role.iam_for_lambda.arn
  source_code_hash    = data.archive_file.lambda.output_base64sha256
  handler             = "lambda_function.lambda_handler"
  runtime             = "python3.8"

  environment {
    variables = {
      DISCORD_TOKEN = ""
    }
  }
  tags = module.label.tags
}

