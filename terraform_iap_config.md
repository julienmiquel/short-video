# Configuring IAP for the Backend Cloud Run Service via Terraform

This document outlines the necessary Terraform configurations to enable Identity-Aware Proxy (IAP) for the backend Cloud Run service and manage its IAM bindings.

## 1. Enabling IAP on the Cloud Run Service

To enable IAP for an existing Cloud Run service, you typically modify its resource definition. If you are using the `google_cloud_run_v2_service` resource, you would manage IAP settings through an `google_iap_web_iam_member` or similar IAP-specific resource, or by configuring an HTTP Load Balancer in front of Cloud Run and enabling IAP on the load balancer's backend service.

However, a more direct way if not using a complex LB setup is to ensure the Cloud Run service itself is configured to only accept authenticated invocations and then set up IAP. The primary IAP configuration is done at the GCP project level or via a Load Balancer.

If a Google Cloud Load Balancer is fronting Cloud Run (which is common for IAP), you would:
*   Enable IAP on the **backend service** associated with the Cloud Run service.
*   Ensure the Cloud Run service itself is configured to allow invocations from this load balancer and potentially only from internal traffic if IAP is the sole entry point.

**Example (Conceptual - assuming `google_compute_backend_service` for a Load Balancer):**

```terraform
# In your backend_service resource for the Load Balancer
resource "google_compute_backend_service" "default" {
  # ... other configurations ...
  project = var.project_id
  name    = "your-backend-service-name"
  
  iap {
    oauth2_client_id          = google_iap_client.project_iap_client.client_id
    oauth2_client_secret      = google_iap_client.project_iap_client.secret
    # oauth2_client_secret_sha256 = # if using secret manager for the client secret
  }
}

# Create an IAP OAuth client if one doesn't exist
resource "google_iap_client" "project_iap_client" {
  project      = var.project_id 
  display_name = "Project IAP Client"
}
```
*(The actual setup might differ based on whether a load balancer is used. If IAP is enabled directly on Cloud Run without an external LB, the focus is more on IAM and the service's ingress settings.)*

Cloud Run's own ingress controls should be set to `internal-and-cloud-load-balancing` if a load balancer is used, or `all` if IAP is configured to work with direct Cloud Run invocations (less common for user-facing auth, but possible).

## 2. IAM Permissions for IAP

Users who need to access the IAP-protected service must be granted the "IAP-secured Web App User" role (`roles/iap.httpsResourceAccessor`) on the IAP-protected resource (e.g., the backend service of the load balancer, or the Cloud Run service if IAP is applied more directly).

**Example Terraform for IAM Binding:**

```terraform
# Granting a user access to the IAP-protected web app
# The resource is the IAP-protected resource itself.
# This could be the project, or a specific backend service, or the Cloud Run service.
# For a backend service used by a global load balancer:
# resource_id would be projects/YOUR_PROJECT_ID/global/backendServices/YOUR_BACKEND_SERVICE_ID
# Or for a Cloud Run service:
# resource_id would be projects/YOUR_PROJECT_ID/locations/YOUR_REGION/services/YOUR_CLOUD_RUN_SERVICE_NAME

resource "google_iap_web_iam_member" "iap_user_access" {
  project = var.project_id # Project where IAP is configured
  # For a backend service:
  # resource_name = "//compute.googleapis.com/projects/${var.project_id}/global/backendServices/${google_compute_backend_service.default.id}" 
  # For Cloud Run directly (less common for user auth, usually via LB):
  # resource_name = "//run.googleapis.com/${google_cloud_run_v2_service.default.id}"
  
  # This example assumes you have a google_compute_backend_service named 'default'
  # You'll need to get the correct resource ID for your IAP-protected entity.
  # This often involves constructing the ID string.
  
  # For example, if IAP is on a backend service:
  # member = "user:user@example.com"
  # role   = "roles/iap.httpsResourceAccessor"
}

# Alternatively, using google_project_iam_member if granting access at project level (broader):
# resource "google_project_iam_member" "iap_access" {
#   project = var.project_id
#   role    = "roles/iap.httpsResourceAccessor"
#   member  = "user:user@example.com"
# }
```
This grants `user@example.com` the necessary role. You can also grant it to Google Groups, service accounts, etc.

## 3. Service Account Permissions for Cloud Run

The Cloud Run service itself needs to be invokable by IAP. If IAP is configured on a Load Balancer, the Load Balancer's Google-managed service account needs rights to invoke your Cloud Run service. If IAP is interacting more directly, the setup ensures the Cloud Run service allows authenticated invocations.

The `google_cloud_run_v2_service` resource has an `ingress` setting. If using IAP via a Load Balancer, this is often set to `INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCING`.
The service also needs IAM policies to allow invocation. The "Cloud Run Invoker" (`roles/run.invoker`) role is key here.

If IAP is enabled, the Cloud Run service's "Authentication" setting should be set to "Allow unauthenticated invocations" if a Load Balancer + IAP is handling authentication *before* requests reach Cloud Run. Cloud Run itself then relies on the IAP-generated JWT passed by the LB. If IAP is more deeply integrated with Cloud Run directly, then Cloud Run might be set to "Require authentication" and IAP acts as the identity provider. The former (LB + IAP, Cloud Run allows unauth) is more common for user-facing web apps.

**Key Environment Variables for the Backend Application:**
Ensure the following environment variables are set for your Cloud Run service:
*   `IAP_VALIDATION_ENABLED="true"`
*   `IAP_EXPECTED_AUDIENCE="/projects/YOUR_PROJECT_NUMBER/apps/YOUR_PROJECT_ID"` (if IAP is project-level for App Engine style, common) OR
*   `IAP_EXPECTED_AUDIENCE="/projects/YOUR_PROJECT_NUMBER/global/backendServices/YOUR_BACKEND_SERVICE_ID"` (if IAP is on a Global Backend Service for a Load Balancer) OR
*   `IAP_EXPECTED_AUDIENCE="URL_OF_YOUR_CLOUD_RUN_SERVICE"` (if IAP is enabled for Cloud Run directly and this is the audience it uses)

The exact audience string (`IAP_EXPECTED_AUDIENCE`) is crucial and can be found by inspecting a valid IAP JWT's `aud` claim once IAP is set up.

**Note:**
Modifying Terraform configurations, especially IAM and IAP settings, should be done with caution and thoroughly tested. This document provides general guidance; specific resource names and configurations will depend on your existing Terraform setup.
