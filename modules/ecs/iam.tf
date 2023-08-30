########################
#         IAM          #
########################
# Give ecs perms to run its tasks
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.label_id}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Effect = "Allow"
        Sid    = ""
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name

  # Attach AWS managed policy to role for necessary ECS task execution permissions
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy" 
}

# ECR Pull image
resource "aws_iam_policy" "ecs_ecr_pull_images" {
  name   = "${var.label_id}-ecs-ecr-pull-images"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability"
        ]
        Resource = "*"
        Effect   = "Allow"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_ecr_pull_images_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.ecs_ecr_pull_images.arn
}

# Allow Access to EC2
resource "aws_iam_policy" "ecs_ec2_management" {
  name   = "${var.label_id}-ecs-ec2-management"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ec2:RunInstances",
          "ec2:StopInstances",
          "ec2:TerminateInstances",
          "ec2:DescribeInstances",
          "ec2:CreateKeyPair",
          "ec2:DeleteKeyPair",
          "ec2:DescribeKeyPairs",
          "ec2:ImportKeyPair"
        ]
        Resource = [
          "arn:aws:ec2:*:*:instance/*",
          "arn:aws:ec2:*:*:key-pair/*",
        ]
        Effect   = "Allow"
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "ecs_ec2_management_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.ecs_ec2_management.arn
}

# Cloud Watch logs
resource "aws_iam_policy" "ecs_cloudwatch_logs" {
  name   = "${var.label_id}-ecs-cloudwatch_logs"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:CreateLogGroup"
        ]
        Resource = "*"
        Effect   = "Allow"
      }
    ]
  })
}

# Cloud Watch Log Group
resource "aws_cloudwatch_log_group" "ecs_log_group" {
  name = "/ecs/${local.container_definition_name}"
  retention_in_days = 1
}

resource "aws_iam_role_policy_attachment" "ecs_cloudwatch_logs_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.ecs_cloudwatch_logs.arn
}

# SSM Parameter Access
resource "aws_iam_policy" "ecs_ssm_access" {
  name   = "${var.label_id}-ecs-ssm-access"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ssm:GetParameter"
        ]
        Resource = [
          "arn:aws:ssm:*:847399026905:parameter/${var.bot_command_name}",
          "arn:aws:ssm:*:847399026905:parameter/${var.ec2_private_key_name}",
          "arn:aws:ssm:*:847399026905:parameter/${var.terraform_token_name}",
          "arn:aws:ssm:*:847399026905:parameter/${var.git_private_key_name}"
        ]
        Effect   = "Allow"
      },
      {
        Action   = [
          "ssm:PutParameter",
        ]
        Effect   = "Allow"
        Resource = [
          "arn:aws:ssm:*:847399026905:parameter/mc_server/private_key",
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_ssm_access_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.ecs_ssm_access.arn
}

# S3 Access
resource "aws_iam_policy" "mc_allow_ecs_to_s3" {
  name = "${var.label_id}-ecs-allow-ecs-to-s3"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = ["${var.s3_bucket_arns}"]
      },
      {
        Effect   = "Allow"
        Action   = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
        ]
        Resource = ["${var.s3_bucket_arns}/*"]
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "mc_allow_ecs_to_s3_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.mc_allow_ecs_to_s3.arn
}