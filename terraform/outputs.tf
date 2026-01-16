output "resource_group_name" {
  value = data.azurerm_resource_group.main.name
}

output "storage_account_name" {
  value = module.storage.account_name
}

output "storage_containers" {
  value = module.storage.containers
}

output "acr_name" {
  value = module.acr.acr_name
}

output "acr_login_server" {
  value = module.acr.acr_login_server
}

output "container_app_name" {
  value = module.container_apps.container_app_name
}

output "log_analytics_name" {
  value = module.container_apps.log_analytics_name
}

output "cosmos_postgres_admin_password" {
  value     = module.cosmos_postgres.admin_password
  sensitive = true
}
