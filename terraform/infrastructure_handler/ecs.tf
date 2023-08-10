########################
#         IAM          #
########################
# Give ecs perms to run its tasks
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecs_${var.name}_task_execution_role"

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
  name   = "ecs_${var.name}_ecr_pull_images"
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
  name   = "ecs_${var.name}_ec2_management"
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
  name   = "ecs_${var.name}_cloudwatch_logs"
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
  name = "/ecs/${var.ecr_image_name}"
  retention_in_days = 1
}

resource "aws_iam_role_policy_attachment" "ecs_cloudwatch_logs_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.ecs_cloudwatch_logs.arn
}

# SSM Parameter Access
resource "aws_iam_policy" "ecs_ssm_access" {
  name   = "ecs_${var.name}_ssm_access"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ssm:GetParameter"
        ]
        Resource = [
          "arn:aws:ssm:*:847399026905:parameter/mc_server/BOT_COMMAND",
          "arn:aws:ssm:*:847399026905:parameter/mc_server/private_key",
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
resource "aws_iam_role_policy" "mc_allow_ecs_to_s3" {
  name   = "${module.label.id}-allow-ecs-to-s3"
  role   = aws_iam_role.ecs_task_execution_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = ["${aws_s3_bucket.mc_s3.id}/*"]
      },
      {
        Effect   = "Allow"
        Action   = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
        ]
        Resource = ["${aws_s3_bucket.mc_s3.id}/*"]
      },
    ]
  })
}

########################
#         ECS          #
########################
resource "aws_ecs_cluster" "my_cluster" {
  name = "${var.name}_cluster"
  tags = module.label.tags
}

resource "aws_ecs_task_definition" "my_task" {
  family                = "${var.name}_task_definition"
  network_mode          = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn    = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn         = aws_iam_role.ecs_task_execution_role.arn

  # Task Level Resource Limits
  cpu                   = var.ecs_cpu_limit
  memory                = var.ecs_memory_limit

  # Container level definiton
  container_definitions = <<DEFINITION
  [
    {
      "name": "${var.ecr_repo_name}",
      "image": "${data.aws_caller_identity.aws.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.ecr_repo_name}:latest",
      "cpu": ${var.ecs_cpu_limit},
      "memory": ${var.ecs_memory_limit},
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/${var.ecr_image_name}",
          "awslogs-region": "${var.aws_region}",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
  DEFINITION

  tags = module.label.tags
}

########################
#         ECR          #
########################
# Minecraft Python infra runner image
resource "aws_ecr_repository" "mc_repository" {
  name                 = var.ecr_repo_name
  image_tag_mutability = "MUTABLE"
  force_delete = true
  
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = module.label.tags
}

resource "aws_ecr_lifecycle_policy" "delete_untagged_images" {
  repository = aws_ecr_repository.mc_repository.name

  policy = <<EOF
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Expire untagged images",
      "selection": {
        "tagStatus": "untagged",
        "countType": "imageCountMoreThan",
        "countNumber": 1
      },
      "action": {
        "type": "expire"
      }
    }
  ]
}
EOF
}

