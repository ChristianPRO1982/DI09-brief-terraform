variable "name" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "tags" {
  type = map(string)
}

variable "admin_username" {
  type = string
}

variable "coordinator_vcore_count" {
  type    = number
  default = 1
}

variable "coordinator_storage_quota_in_mb" {
  type    = number
  default = 32768
}

variable "coordinator_server_edition" {
  type    = string
  default = "BurstableMemoryOptimized"
}
