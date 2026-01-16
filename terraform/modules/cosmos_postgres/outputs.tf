output "host" {
  value = azurerm_cosmosdb_postgresql_cluster.main.servers[0].fqdn
}

output "port" {
  value = 5432
}

output "db_name" {
  value = "citus"
}

output "admin_username" {
  value = var.admin_username
}

output "admin_password" {
  value     = random_password.admin.result
  sensitive = true
}
