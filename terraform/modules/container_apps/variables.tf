variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "acr_login_server" {
  type = string
}

variable "acr_username" {
  type = string
  sensitive = true
}

variable "acr_password" {
  type = string
  sensitive = true
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "cpu" {
  type    = number
  default = 0.5
}

variable "memory" {
  type    = string
  default = "1Gi"
}

variable "min_replicas" {
  type    = number
  default = 0
}

variable "max_replicas" {
  type    = number
  default = 1
}
