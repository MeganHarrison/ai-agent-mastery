provider "google" {
  project = var.project_id
  region  = var.region
}
provider "google-beta" {
  project = var.project_id
  region  = var.region
}

################  Artifact Registry  ################
resource "google_artifact_registry_repository" "docker" {
  location      = var.region
  repository_id = "docker-artifacts"
  format        = "DOCKER"
}

################  Static-site bucket + HTTPS LB  ####
resource "google_storage_bucket" "frontend" {
  name                        = var.frontend_domain       # must match domain
  location                    = "US"
  uniform_bucket_level_access = true
  website {
    main_page_suffix = "index.html"
    not_found_page   = "index.html"
  }
}

resource "google_compute_managed_ssl_certificate" "frontend_ssl" {
  name    = "frontend-ssl"
  managed { domains = [var.frontend_domain] }
}

module "lb_site" {
  source  = "terraform-google-modules/cloud-foundation-fabric/google//modules/lb-http"
  version = "6.4.0"

  project_id = var.project_id
  name       = "frontend-lb"
  ssl        = true

  certificate_map = {
    (var.frontend_domain) = google_compute_managed_ssl_certificate.frontend_ssl.name
  }
  backends = {
    default = { backend_bucket = google_storage_bucket.frontend.name }
  }
  host_rules = [
    { hosts = [var.frontend_domain], path_matcher = "allpaths" }
  ]
}

################  Cloud Run service (Agent API) #####
resource "google_cloud_run_v2_service" "agent" {
  name     = "backend-agent-api"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}/backend_agent_api:latest"
      ports { container_port = 8001 }
      env   = [for k, v in var.agent_env : { name = k, value = v }]
    }
  }
  traffic { percent = 100, latest_revision = true }
}

resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  service  = google_cloud_run_v2_service.agent.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

################  Cloud Run job (RAG)  ##############
resource "google_cloud_run_v2_job" "rag" {
  provider = google-beta
  name     = "backend-rag-pipeline"
  location = var.region

  template {
    template {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}/backend_rag_pipeline:latest"
        env   = [for k, v in var.rag_env : { name = k, value = v }]
      }
      max_retries = 0
      timeout     = "900s"
    }
  }
}

# SA for scheduler → job
resource "google_service_account" "scheduler" {
  account_id   = "rag-scheduler"
  display_name = "Scheduler invoker"
}
resource "google_cloud_run_v2_job_iam_member" "invoke_from_scheduler" {
  provider = google-beta
  name     = google_cloud_run_v2_job.rag.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler.email}"
}

################  Cloud Scheduler trigger  ###########
resource "google_cloud_scheduler_job" "rag_trigger" {
  name     = "rag-every-10m"
  region   = var.region
  schedule = "*/10 * * * *"

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.rag.name}:run"
    oidc_token  { service_account_email = google_service_account.scheduler.email }
  }
}

################  Domain mapping (API)  ##############
resource "google_cloud_run_domain_mapping" "api_domain" {
  name     = var.api_domain
  location = var.region
  metadata { namespace = var.project_id }
  spec     { route_name = google_cloud_run_v2_service.agent.name }
}

################  Outputs  ###########################
output "frontend_url" { value = "https://${var.frontend_domain}" }
output "api_url"      { value = "https://${var.api_domain}" }
