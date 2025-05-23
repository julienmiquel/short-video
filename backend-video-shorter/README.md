# Backend Video Shorter Service

This service provides APIs to create short video clips from YouTube videos and generate thumbnail highlights using AI.

## API Endpoints

### `GET /ping`

A simple health check endpoint.

**Example Success Response (200 OK):**

```json
{
    "msg": "ping"
}
```

### `POST /generate_highlights`

Analyzes a YouTube video and suggests timestamps suitable for thumbnails or marketing campaigns.

**Request Body:**

*   `youtube_url` (string, required): The URL of the YouTube video.

**Example Request:**

```json
{
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Example Success Response (200 OK):**
*(Note: The actual highlight content will vary based on AI analysis.)*

```json
{
    "clip_path": null,
    "message": "Highlights generated",
    "highlights": {
        "highlights": [
            {
                "timestamp": "0:15",
                "reasoning": "Good frame for thumbnail"
            },
            {
                "timestamp": "1:02",
                "reasoning": "Frame captures peak action or expression."
            }
        ]
    }
}
```

### `POST /create_clip`

Creates a video clip from a specified YouTube URL, start time, and duration.

**Request Body:**

*   `youtube_url` (string, required): The URL of the YouTube video.
*   `start_time` (integer, required): Start time of the clip in seconds.
*   `duration` (integer, required): Duration of the clip in seconds.
*   `clip_name` (string, optional): Desired name for the output clip file (without extension). Defaults to "clip".

**Example Request:**

```json
{
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "start_time": 10,
    "duration": 5,
    "clip_name": "my_rick_roll_segment"
}
```

**Example Success Response (200 OK):**
*(Note: Based on the current implementation where `ClipCreator.create_clip` returns `ClipResponse(clip_path=output_path)`, the `message` field defaults to `null` if `ClipResponse.message` is `Optional[str] = None`, and `highlights` defaults to an empty list structure if `ClipResponse.highlights` has a `default_factory`.)*

```json
{
    "clip_path": "clips/my_rick_roll_segment.mp4",
    "message": null,
    "highlights": {
        "highlights": []
    }
}
```

## Configuration (Environment Variables)

The service uses the following environment variables for configuration. These are defined in `backend/config.py` and loaded via the `Settings` class.

*   **`DOWNLOAD_DIR`**
    *   Description: Directory to store downloaded YouTube videos before processing.
    *   Default: `"downloads"`
*   **`OUTPUT_DIR`**
    *   Description: Directory to store the created video clips.
    *   Default: `"clips"`
*   **`FFMPEG_PATH`**
    *   Description: Path to the ffmpeg executable.
    *   Default: `"ffmpeg"`
*   **`VERTEX_AI_PROJECT_ID`**
    *   Description: Google Cloud Project ID for Vertex AI services, used for highlight generation.
    *   Default: `"ml-demo-384110"`
*   **`VERTEX_AI_LOCATION`**
    *   Description: Google Cloud Location (region) for Vertex AI services.
    *   Default: `"us-central1"`

## Running Locally

### Prerequisites

*   Python 3.10+
*   Poetry (for dependency management and running scripts)

### Installation

1.  Clone the repository.
2.  Navigate to the `backend-video-shorter` directory (or the root of the backend project where `pyproject.toml` is located).
3.  Install dependencies using Poetry:
    ```bash
    poetry install
    ```
    This command installs all dependencies, including development dependencies, as specified in `poetry.lock` (if present) or `pyproject.toml`.

### Running the Service

Once dependencies are installed, you can run the FastAPI service using Uvicorn. The `pyproject.toml` file might contain a script to run the server, or you can run it directly:

```bash
poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

*   `--reload`: Enables auto-reload when code changes, which is useful for development.
*   `--host 0.0.0.0`: Makes the service accessible from your local network (not just `localhost`).
*   `--port 8000`: Specifies the port the service will run on.

The service will then be available at `http://localhost:8000`.

## Running Tests

To run the unit tests for the backend service:

1.  Ensure you are in the directory containing the `pyproject.toml` file for the backend.
2.  Execute the following command:

    ```bash
    poetry run pytest
    ```
This command will discover and run all tests defined in the `tests` directory.
