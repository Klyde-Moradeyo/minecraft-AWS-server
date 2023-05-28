########################
#         IAM          #
########################

# ECR Pull image
resource "aws_iam_policy" "ecs_ecr_pull_images" {
  name   = "ecs_${var.name}_ecr_pull_images"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
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

# Allow Access to EC2
resource "aws_iam_policy" "ecs_ec2_management" {
  name   = "ecs_${var.name}_ec2_management"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ec2:Create*",
          "ec2:Delete*",
          "ec2:Modify*"
        ]
        Resource = "*"
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

  # Task Level Resource Limits
  cpu                   = var.ecs_cpu_limit
  memory                = var.ecs_memory_limit

  # Container level definiton
  container_definitions = <<DEFINITION
  [
    {
      "name": "${var.ecr_repo_name}",
      "image": "${data.aws_caller_identity.aws.account_id}.dkr.ecr.${var.region}.amazonaws.com/${var.ecr_repo_name}/${var.ecr_image_name}:latest",
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
