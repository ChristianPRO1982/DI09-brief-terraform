variable "project_name" {
  type        = string
  description = "Project short name (e.g. nyctaxi)"
}

variable "environment" {
  type        = string
  description = "Environment name (e.g. dev)"
}

variable "location" {
  type        = string
  description = "Azure region"
  default     = "francecentral"
}

variable "tags" {
  type        = map(string)
  description = "Resource tags"
  default     = {}
}

variable "resource_group_name" {
  type        = string
  description = "Existing Resource Group name where resources will be deployed"
}

variable "container_apps_cpu" {
  type        = number
  description = "Container Apps CPU"
  default     = 0.5
}

variable "container_apps_memory" {
  type        = string
  description = "Container Apps Memory"
  default     = "1Gi"
}

variable "container_apps_min_replicas" {
  type        = number
  description = "Min replicas"
  default     = 0
}

variable "container_apps_max_replicas" {
  type        = number
  description = "Max replicas"
  default     = 1
}

variable "cosmos_db_admin_username" {
  type        = string
  description = "Admin username for Cosmos DB for PostgreSQL."
  default     = "citus"
}

variable "subscription_id" {
  type        = string
  description = "5e2150ec-ee17-4fa2-8714-825c2fb7d22a"
}

