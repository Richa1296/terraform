resource "google_storage_bucket" "scripts" {
  name     = "upload_scripts_from_terraform"
  location = "US-CENTRAL1"
}

resource "google_storage_bucket_object" "script" {
  name   = "scripts/create_iceberg_data.py"
  source = "create_iceberg_data.py"
  bucket = "demobucket_na"
}
