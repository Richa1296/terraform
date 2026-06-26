terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.7.0"
    }
  }
}
provider "google" {
  project = "payments-dev-495611"
  region = "us-cenral1"
  zone = "us-central1-a"
}

resource "google_storage_bucket" "GCS1"{
  name = "bucket_from_terraform"
}
