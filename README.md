# short-video

Make short video easily

## Instructions

### TL;DR

#### Setup

### Production Deployment with Terraform

**Quick Start:**

1. Enable required APIs in the CI/CD project.

   ```bash
   gcloud config set project YOUR_CI_CD_PROJECT_ID
   gcloud services enable serviceusage.googleapis.com cloudresourcemanager.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com
   ```

2. Create a Git repository (GitHub, GitLab, Bitbucket).
3. Connect to Cloud Build following [Cloud Build Repository Setup](https://cloud.google.com/build/docs/repositories#whats_next).
4. Configure [`deployment/terraform/vars/env.tfvars`](deployment/terraform/vars/env.tfvars) with your project details.
5. Deploy infrastructure:

   ```bash
   cd deployment/terraform
   terraform init
   terraform apply --var-file vars/env.tfvars
   ```

6. Perform a commit and push to the repository to see the CI/CD pipelines in action!

For detailed deployment instructions, refer to [deployment/README.md](deployment/README.md).


## Help welcome

PRs welcome to add extra features such as logging / monitoring / etc.

### Features / Technologies Used

1. [Cloud Run](https://cloud.google.com/run)
2. [Vertex AI](https://cloud.google.com/vertex-ai)
