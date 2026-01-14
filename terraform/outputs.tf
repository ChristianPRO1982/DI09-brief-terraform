output "resource_group_name" {
  value = data.azurerm_resource_group.main.name
}

output "storage_account_name" {
  value = module.storage.account_name
}

output "storage_containers" {
  value = module.storage.containers
}
