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
