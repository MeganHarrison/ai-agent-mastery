terraform {
  required_version = ">= 1.7"
  required_providers {
    google       = { source = "hashicorp/google",       version = "~> 5.21" }
    google-beta  = { source = "hashicorp/google-beta",  version = "~> 5.21" }
  }

  # backend bucket created manually the first time (skip if you prefer local state)
  backend "gcs" {
    bucket = "tfstate-${var.project_id}"
    prefix = "prod"
  }
}
