# Cloud Scheduler - Automate tasks on a schedule

# Service Account for Cloud Scheduler
resource "google_service_account" "scheduler_sa" {
  account_id   = "cloud-scheduler-sa"
  display_name = "Cloud Scheduler Service Account"
}

# Grant Cloud Scheduler permission to invoke Cloud Run
resource "google_cloud_run_service_iam_member" "scheduler_run_invoker" {
  service       = google_cloud_run_service.run-app-from-tf.name
  location      = google_cloud_run_service.run-app-from-tf.location
  role          = "roles/run.invoker"
  member        = "serviceAccount:${google_service_account.scheduler_sa.email}"
}

# Cloud Scheduler Job - Runs daily at 10 AM IST
resource "google_cloud_scheduler_job" "daily_job" {
  name            = "daily-task-scheduler"
  description     = "Run Cloud Run service daily"
  schedule        = "0 4 * * *"  # 4 AM UTC = 10 AM IST (UTC+5:30)
  time_zone       = "UTC"
  attempt_deadline = "320s"
  region          = "us-central1"

  # HTTP Target - invoke Cloud Run
  http_target {
    uri        = "${google_cloud_run_service.run-app-from-tf.status[0].url}/"
    http_method = "GET"

    # Use service account for authentication
    oidc_token {
      service_account_email = google_service_account.scheduler_sa.email
    }

    headers = {
      "User-Agent" = "Google-Cloud-Scheduler"
    }
  }

  # Enable the job
  depends_on = [
    google_cloud_run_service_iam_member.scheduler_run_invoker,
    google_service_account.scheduler_sa
  ]
}

# Outputs
output "scheduler_job_name" {
  value       = google_cloud_scheduler_job.daily_job.name
  description = "Name of the scheduled job"
}

output "scheduler_service_account" {
  value       = google_service_account.scheduler_sa.email
  description = "Service account used by scheduler"
}

output "schedule_cron" {
  value       = google_cloud_scheduler_job.daily_job.schedule
  description = "Cron expression for the schedule"
}
