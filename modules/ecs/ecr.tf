########################
#         ECR          #
########################
# Minecraft Python infra runner image
resource "aws_ecr_repository" "mc_repository" {
  name                 = "${var.label_id}-${var.ecr_repo_name}"
  image_tag_mutability = "MUTABLE"
  force_delete = true
  
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = var.label_tags
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