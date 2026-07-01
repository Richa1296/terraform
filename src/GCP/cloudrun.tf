resource "google_cloud_run_service" "run-app-from-tf" {
  location = "asia-southeast1"
  name     = "run-app-from-tf"

  template {
    spec {
      containers {
        image = "gcr.io/google-samples/hello-app:2.0"
      }
    }
  }
  traffic {
    percent = 50
    revision_name = "run-app-from-tf-00001-wjb"
  }
  traffic {
    percent = 50
    revision_name = "run-app-from-tf-00002-k4n"
  }
}

resource "google_cloud_run_service_iam_policy" "pub_access" {
  policy_data   = data.google_iam_policy.pub-1.policy_data
  service       = google_cloud_run_service.run-app-from-tf.name
  location      = google_cloud_run_service.run-app-from-tf.location
}

data "google_iam_policy" "pub-1" {
  binding {
    members = ["allUsers"]
    role    = "roles/run.invoker"
  }
}