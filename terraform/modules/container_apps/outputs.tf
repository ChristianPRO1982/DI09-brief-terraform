output "container_app_name" {
  value = azurerm_container_app.main.name
}

output "log_analytics_name" {
  value = azurerm_log_analytics_workspace.main.name
}
