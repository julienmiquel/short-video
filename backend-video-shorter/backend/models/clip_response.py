from pydantic import BaseModel  # For data validation
from typing import List, Dict


class Highlight(BaseModel):
    timestamp: str
    reasoning: str

class Highlights(BaseModel):
    highlights : List[Highlight] = []

    def __init__(self, arr):
        super().__init__()

        self.highlights = [Highlight(timestamp=h['timestamp'], reasoning=h['reasoning']) for h in arr]

    
# Data models using Pydantic
class ClipResponse(BaseModel):
    message: str
    clip_path: str | None = None  # clip_path is optional
    highlights : Highlights
