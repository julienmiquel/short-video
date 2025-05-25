# Testing Backend IAP Integration

This document provides guidance on how to test the Identity-Aware Proxy (IAP) integration with the backend Cloud Run service. These steps assume IAP has been configured for your Cloud Run service as per the `terraform_iap_config.md` document, and your backend code includes the IAP validation middleware.

## Prerequisites

1.  **IAP Configured:** IAP is enabled for your Cloud Run service, and you have specified the OAuth 2.0 Client ID and Secret.
2.  **User Permissions:** The Google account you are testing with has the "IAP-secured Web App User" (`roles/iap.httpsResourceAccessor`) permission for the IAP-protected Cloud Run service.
3.  **`gcloud` CLI:** Google Cloud CLI is installed and authenticated with the user account that has IAP access.
4.  **Environment Variables Set for Backend:**
    *   `IAP_VALIDATION_ENABLED="true"` (on the deployed Cloud Run service)
    *   `IAP_EXPECTED_AUDIENCE` (set to the correct audience string for your IAP setup, e.g., `/projects/YOUR_PROJECT_NUMBER/apps/YOUR_PROJECT_ID` or the URL of the Cloud Run service if that's what IAP uses for its `aud` claim).
5.  **Service URL:** The URL of your deployed IAP-protected Cloud Run service.

## Testing Steps

### 1. Obtain an IAP ID Token

You can obtain an ID token for your user account that can be used to access an IAP-protected application by using the `gcloud` CLI. The Client ID required here is the OAuth 2.0 Client ID that was configured for IAP.

```bash
# First, find your OAuth 2.0 Client ID used by IAP. 
# You can find this in the GCP Console under "APIs & Services" > "Credentials",
# or it's the client ID referenced in your IAP Terraform setup (e.g., from `google_iap_client`).

# Let's say your OAuth Client ID is: YOUR_IAP_OAUTH_CLIENT_ID.apps.googleusercontent.com

gcloud auth print-identity-token --audiences="YOUR_IAP_OAUTH_CLIENT_ID.apps.googleusercontent.com"
```

This command will print an ID token (a long JWT string) to the console. Copy this token.

**Note:** This token is for the *OAuth client ID* that IAP uses, not directly for the backend service's audience. IAP itself will then issue its own JWT (`X-Goog-IAP-JWT-Assertion`) to the backend, and that JWT will have the `IAP_EXPECTED_AUDIENCE`. The token obtained via `gcloud auth print-identity-token` is used to authenticate *to IAP*.

### 2. Accessing the IAP-Protected Service

#### Test Case 2.1: Accessing via a Browser (Intended Flow)

*   Open a web browser where you are logged into the Google account that has IAP access permissions.
*   Navigate to the URL of your IAP-protected Cloud Run service (e.g., `https://your-service-name-xyz.a.run.app/ping`).
*   IAP should intercept the request, authenticate you via your Google session, and then forward the request to your backend along with the `X-Goog-IAP-JWT-Assertion` header.
*   The `/ping` endpoint should return a response like:
    ```json
    {
        "msg": "ping",
        "user": "your.email@example.com" 
    }
    ```
    This verifies that the middleware correctly validated the IAP JWT and extracted your email.

#### Test Case 2.2: Accessing Programmatically with a Valid IAP-Generated Token (Simulating IAP)

This test is more direct for verifying the backend's handling of the `X-Goog-IAP-JWT-Assertion` header. To do this properly, you'd ideally capture a real `X-Goog-IAP-JWT-Assertion` header sent by IAP (e.g., by temporarily logging it in your backend when accessed via browser).

However, if you want to test the *backend logic* assuming IAP *would* provide a token, and you have a way to generate a token that *mimics* an IAP token (this is hard without being IAP), this is where it gets tricky. The token from `gcloud auth print-identity-token` is *not* the same as the `X-Goog-IAP-JWT-Assertion` header value.

The most reliable way to test the backend's JWT validation is through the browser (Test Case 2.1) or by having an automated test that can perform an OAuth2 flow against IAP.

If you are testing the *middleware's parsing logic* and have a sample (even expired) `X-Goog-IAP-JWT-Assertion` token, you could use `curl` or Postman:

```bash
# This assumes you have a captured IAP_JWT_TOKEN from a previous successful IAP auth
IAP_JWT_TOKEN="your_captured_X-Goog-IAP-JWT-Assertion_token"
SERVICE_URL="https://your-service-name-xyz.a.run.app/ping"

curl -H "X-Goog-IAP-JWT-Assertion: ${IAP_JWT_TOKEN}" "${SERVICE_URL}"
```
If the token is valid and the audience matches, it should return your user email. If the token is invalid/expired, it should return a 401 error.

#### Test Case 2.3: Accessing Without IAP Authentication

*   **If `IAP_VALIDATION_ENABLED` is "true" on the service:**
    *   Attempt to access the service URL directly with `curl` without any IAP headers:
        ```bash
        curl -v "https://your-service-name-xyz.a.run.app/ping"
        ```
    *   **Expected:** IAP itself (at the Google Front End / Load Balancer level) should block this request, likely with a 302 redirect to Google Accounts or a 401/403 error, before it even reaches your Cloud Run instance. If it *does* reach your instance without the header, your middleware should return a 401 due to "Missing IAP JWT Assertion".
*   **If `IAP_VALIDATION_ENABLED` is "false" (local development mode):**
    *   The middleware will bypass validation, and the `/ping` endpoint should return:
        ```json
        {
            "msg": "ping",
            "user": "local_dev_user@example.com"
        }
        ```

### 3. Verifying Negative Cases (Backend Logic)

If you could mock the IAP header with invalid content (difficult without deploying modified code or using a sophisticated local proxy):
*   **Invalid Token:** Send a garbage string in `X-Goog-IAP-JWT-Assertion`. Expected: 401 "Invalid IAP JWT".
*   **Mismatched Audience:** If the `IAP_EXPECTED_AUDIENCE` on the server doesn't match the `aud` claim in a (hypothetically valid) JWT. Expected: 401 "Invalid IAP JWT".

These negative cases for the backend logic are often best covered by unit tests for the middleware, where you can directly control the input headers and environment variables.

## Summary

*   The primary end-to-end test is accessing the IAP-protected URL through a browser with an authenticated user session.
*   Check service logs for any errors related to IAP validation or audience mismatch.
*   Ensure `IAP_VALIDATION_ENABLED="true"` and the correct `IAP_EXPECTED_AUDIENCE` are set in the Cloud Run service environment for production/staging.
```
