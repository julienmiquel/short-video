from pydantic import BaseModel  # For data validation

# Data models using Pydantic
class ClipRequest(BaseModel):
    youtube_url: str
    start_time: int | None = None  # clip_name is optional
    duration: int | None = None  # clip_name is optional
    clip_name: str | None = None  # clip_name is optional