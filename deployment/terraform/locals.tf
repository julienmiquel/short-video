locals {
  apis = [
    # Cloud Build for App Hosting
    "cloudbuild.googleapis.com",
    # Secret Manager for App Hosting
    "secretmanager.googleapis.com",
    # To configure user policies
    "iam.googleapis.com",
    # Allow creation of API keys (for maps)
    "apikeys.googleapis.com",
    # For App Hosting
    "orgpolicy.googleapis.com",
    # Vertex AI for Gemini & Imagen
    "aiplatform.googleapis.com",
    # App Hosting Repo Connect
    "developerconnect.googleapis.com",
  ]

  cicd_services = [
    "cloudbuild.googleapis.com",
    "discoveryengine.googleapis.com",
    "aiplatform.googleapis.com",
    "serviceusage.googleapis.com",
    "bigquery.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "cloudtrace.googleapis.com"
  ]

  shared_services = [
    "aiplatform.googleapis.com",
    "run.googleapis.com",
    "discoveryengine.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "bigquery.googleapis.com",
    "serviceusage.googleapis.com",
    "logging.googleapis.com",
    "cloudtrace.googleapis.com"
  ]

  deploy_project_ids = {
    prod    = var.prod_project_id
    staging = var.staging_project_id
  }

  all_project_ids = [
    var.cicd_runner_project_id,
    var.prod_project_id,
    var.staging_project_id
  ]
}