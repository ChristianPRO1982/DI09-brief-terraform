resource "azurerm_log_analytics_workspace" "main" {
  name                = "law-${var.project_name}-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = var.tags
}

resource "azurerm_container_app_environment" "main" {
  name                       = "cae-${var.project_name}-${var.environment}"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  tags = var.tags
}

resource "azurerm_container_app" "main" {
  name                         = "ca-${var.project_name}-pipeline-${var.environment}"
  resource_group_name          = var.resource_group_name
  container_app_environment_id = azurerm_container_app_environment.main.id
  revision_mode                = "Single"

  secret {
    name  = "acr-password"
    value = var.acr_password
  }

  registry {
    server               = var.acr_login_server
    username             = var.acr_username
    password_secret_name = "acr-password"
  }

  template {
    container {
      name   = "pipeline"
      image  = "${var.acr_login_server}/nyc-taxi-pipeline:latest"
      cpu    = var.cpu
      memory = var.memory
    }

    min_replicas = var.min_replicas
    max_replicas = var.max_replicas
  }

  tags = var.tags
}
