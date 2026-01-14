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
