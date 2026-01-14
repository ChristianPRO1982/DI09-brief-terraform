data "azurerm_resource_group" "main" {
  name = var.resource_group_name
}

module "storage" {
  source              = "./modules/storage"
  project_name        = var.project_name
  environment         = var.environment
  resource_group_name = data.azurerm_resource_group.main.name
  location            = data.azurerm_resource_group.main.location
  tags                = var.tags
}

module "acr" {
  source              = "./modules/acr"
  project_name        = var.project_name
  environment         = var.environment
  resource_group_name = data.azurerm_resource_group.main.name
  location            = data.azurerm_resource_group.main.location
  tags                = var.tags
}

module "container_apps" {
  source              = "./modules/container_apps"
  project_name        = var.project_name
  environment         = var.environment
  resource_group_name = data.azurerm_resource_group.main.name
  location            = data.azurerm_resource_group.main.location
  tags                = var.tags

  acr_login_server = module.acr.acr_login_server
  acr_username     = module.acr.acr_admin_username
  acr_password     = module.acr.acr_admin_password

  cpu          = var.container_apps_cpu
  memory       = var.container_apps_memory
  min_replicas = var.container_apps_min_replicas
  max_replicas = var.container_apps_max_replicas
}

