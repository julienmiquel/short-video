# app.py (Main application)
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

from .clip_creator import ClipCreator
from .models.clip_request import ClipRequest  # Import the model
from .models.clip_response import ClipResponse  # Import the model

from pydantic import ValidationError


app = FastAPI()
clip_creator = ClipCreator()  # Initialize the clip creator


@app.get("/ping")
async def ping():
    return {"msg": "ping"}

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
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

    