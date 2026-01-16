resource "random_password" "admin" {
  length  = 24
  special = true
}

resource "azurerm_cosmosdb_postgresql_cluster" "main" {
  name                = var.name
  resource_group_name = var.resource_group_name
  location            = var.location
  tags                = var.tags

  administrator_login_password = random_password.admin.result

  coordinator_vcore_count         = var.coordinator_vcore_count
  coordinator_storage_quota_in_mb = var.coordinator_storage_quota_in_mb
  coordinator_server_edition      = var.coordinator_server_edition

  node_count = 0
}

resource "azurerm_cosmosdb_postgresql_firewall_rule" "allow_azure" {
  name       = "allow-azure-services"
  cluster_id = azurerm_cosmosdb_postgresql_cluster.main.id

  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}
