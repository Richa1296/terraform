# resource "google_compute_instance" "custom_engine" {
#   name         = "custom-engine-instance"
#   machine_type = "e2-micro"
#   zone         = "us-central1-a"
#
#   boot_disk {
#     initialize_params {
#       image = "debian-cloud/debian-12"
#       size  = 20
#     }
#   }
#
#   network_interface {
#     network = "default"
#
#     access_config {
#       # Ephemeral public IP
#     }
#   }
#
#   metadata = {
#     enable-oslogin = "true"
#   }
#
#   tags = ["http-server", "https-server"]
#
#   # Optional: Add startup script
#   metadata_startup_script = <<-EOT
#               #!/bin/bash
#               echo "Custom engine instance started" > /var/log/startup.log
#             EOT
#
#   labels = {
#     environment = "dev"
#     application = "terraform-demo"
#   }
# }
#
# # Output the instance details
# output "instance_name" {
#   value       = google_compute_instance.custom_engine.name
#   description = "Name of the Compute Engine instance"
# }
#
# output "instance_id" {
#   value       = google_compute_instance.custom_engine.id
#   description = "Instance ID"
# }
#
# output "instance_self_link" {
#   value       = google_compute_instance.custom_engine.self_link
#   description = "Self link of the instance"
# }
#
# output "instance_public_ip" {
#   value       = google_compute_instance.custom_engine.network_interface[0].access_config[0].nat_ip
#   description = "Public IP address of the instance"
# }
