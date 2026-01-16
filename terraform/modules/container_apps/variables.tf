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
  type      = string
  sensitive = true
}

variable "acr_password" {
  type      = string
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

variable "postgres_host" { type = string }
variable "postgres_port" { type = number }
variable "postgres_db" { type = string }
variable "postgres_user" { type = string }
variable "postgres_password" { type = string }
variable "postgres_ssl_mode" { type = string }

variable "start_date" {
  type = string
}
