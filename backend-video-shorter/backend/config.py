import os

class Settings:
    DOWNLOAD_DIR: str = os.environ.get("DOWNLOAD_DIR", "downloads")
    OUTPUT_DIR: str = os.environ.get("OUTPUT_DIR", "clips")
    FFMPEG_PATH: str = os.environ.get("FFMPEG_PATH", "ffmpeg")
    VERTEX_AI_PROJECT_ID: str = os.environ.get("VERTEX_AI_PROJECT_ID", "ml-demo-384110")
    VERTEX_AI_LOCATION: str = os.environ.get("VERTEX_AI_LOCATION", "us-central1")

settings = Settings() # Create an instance for easy import
