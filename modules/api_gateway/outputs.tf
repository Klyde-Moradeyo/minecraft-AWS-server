########################
#     API Gateway      #
########################
output "api_gateway_url" {
  value = aws_apigatewayv2_api.minecraft_http_api.api_endpoint
}