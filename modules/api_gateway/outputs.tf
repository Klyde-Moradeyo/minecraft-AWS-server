########################
#     API Gateway      #
########################
output "api_gateway_url" {
  value = aws_apigatewayv2_api.minecraft_http_api.api_endpoint
}

output "stage_name" {
  description = "The name of the deployed stage"
  value       = aws_apigatewayv2_stage.minecraft_stage.name
}