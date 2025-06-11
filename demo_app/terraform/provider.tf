terraform {
  required_version = "~> 1.11"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6"
    }
  }
}

provider "google" {
  project = local.gcp_project
  region  = local.gcp_region
}
