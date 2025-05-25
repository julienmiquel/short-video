# app.py (Main application)
import os # Added
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn
# Imports for IAP Middleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseFunction # Added
from starlette.responses import Response # Added
from google.oauth2 import id_token # Added
from google.auth.transport import requests as google_auth_requests # Added

from .clip_creator import ClipCreator
from .models.clip_request import ClipRequest  # Import the model
from .models.clip_response import ClipResponse  # Import the model

from pydantic import BaseModel, ValidationError # Added BaseModel


app = FastAPI()

# IAP Validation Middleware Definition
class IAPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseFunction) -> Response:
        # Allow skipping IAP validation for local dev/testing if env var is set
        if os.environ.get("IAP_VALIDATION_ENABLED", "false").lower() != "true":
            request.state.user_email = "local_dev_user@example.com" # Dummy user for local dev
            response = await call_next(request)
            return response

        iap_jwt = request.headers.get("X-Goog-IAP-JWT-Assertion")
        if not iap_jwt:
            # For a stricter setup, you'd return 401 here.
            return Response("Missing IAP JWT Assertion", status_code=401)

        try:
            expected_audience = os.environ.get("IAP_EXPECTED_AUDIENCE")
            if not expected_audience:
                # Log this error, as it's a config issue.
                print("ERROR: IAP_EXPECTED_AUDIENCE environment variable not set.")
                return Response("IAP configuration error", status_code=500)

            decoded_token = id_token.verify_iap_jwt(
                iap_jwt,
                audience=expected_audience
            )
            # 'sub' and 'email' should be available in the decoded token
            request.state.user_email = decoded_token.get("email", "unknown_iap_user@example.com")
        
        except Exception as e:
            # Log the validation exception e
            print(f"IAP JWT Validation Error: {e}")
            return Response(f"Invalid IAP JWT: {e}", status_code=401)

        response = await call_next(request)
        return response

# Add the middleware to the FastAPI app
app.add_middleware(IAPMiddleware)

clip_creator = ClipCreator()  # Initialize the clip creator


@app.get("/ping")
async def ping(request: Request): # Add request: Request
    user = getattr(request.state, "user_email", "anonymous")
    return {"msg": "ping", "user": user}

@app.post("/generate_highlights", response_model=ClipResponse) # Add response model
async def generate_highlights(request: Request):
    data = ClipRequest(**await request.json())  # Validate request data
    print(data)
    response = await clip_creator.generate_highlights(data)
    return JSONResponse(content=response.model_dump(), status_code=200) 

@app.post("/create_clip", response_model=ClipResponse) # Add response model
async def create_clip(request: Request):
    try:
        data = ClipRequest(**await request.json())  # Validate request data
        clip_path = await clip_creator.create_clip(data)
        return ClipResponse(message="Clip created successfully", clip_path=clip_path) # Create response object
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # For generic exceptions, ensure a consistent JSON structure.
        # The IAPMiddleware's 500 error for config issues returns: Response("IAP configuration error", status_code=500)
        # which is plain text. For consistency or if more detail is needed:
        return JSONResponse(content={"error": "An unexpected error occurred", "detail": str(e)}, status_code=500)

# Pydantic model for the /api/me response
class UserResponse(BaseModel):
    email: str | None # Allow None if user might not be found or for non-IAP access

@app.get("/api/me", response_model=UserResponse)
async def get_current_user(request: Request):
    # The IAPMiddleware sets request.state.user_email
    # It defaults to "local_dev_user@example.com" if IAP_VALIDATION_ENABLED is not true
    # It might be None if IAP is enabled but somehow a request slips through without the header 
    # (though middleware tries to prevent this by returning 401 if header is missing and IAP is on)
    user_email = getattr(request.state, "user_email", None) 
    
    # If IAP is supposed to be enabled and we still don't have an email,
    # it could indicate a bypass or misconfiguration not caught by middleware's header check.
    if user_email is None and os.environ.get("IAP_VALIDATION_ENABLED", "false").lower() == "true":
        # This case implies IAP is on, but user_email wasn't set by middleware.
        # This might happen if a request somehow bypassed the part of middleware that sets user_email
        # or if the default "unknown_iap_user@example.com" was overridden to None.
        # The middleware itself returns 401 if X-Goog-IAP-JWT-Assertion is missing when IAP_VALIDATION_ENABLED is true.
        # So, reaching here with user_email=None when IAP is on is unlikely unless middleware logic changes.
        raise HTTPException(status_code=401, detail="User not authenticated by IAP or email not available")
        
    return UserResponse(email=user_email)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

    