output "account_name" {
  value = azurerm_storage_account.main.name
}

output "containers" {
  value = {
    raw       = azurerm_storage_container.raw.name
    processed = azurerm_storage_container.processed.name
  }
}
