from fastapi import FastAPI
import unittest.mock # Added
from fastapi.testclient import TestClient


from backend.models.clip_request import ClipRequest
# Import response model and the app's clip_creator instance
import os # Added
import pytest # Added for async def tests if needed by runner
from backend.models.clip_response import ClipResponse, Highlights # Added
from backend.clip_creator import ClipCreator # Ensure ClipCreator is imported
from backend.config import settings # Added for centralized settings
from backend.main import app, clip_creator as main_app_clip_creator # Added main_app_clip_creator

client = TestClient(app)


def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"msg": "ping"}



def test_generate_highlights():
    data = {  # Example data
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  
    }
    response = client.post("/generate_highlights", json=data)
    assert response.status_code == 200
    assert response.json()["message"] == "Highlights generated"


def test_create_clip():
    data = {  # Example data
        "youtube_url": "http://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Replace with a real URL for manual tests
        "start_time": 10,
        "duration": 5,
    }
@unittest.mock.patch.object(main_app_clip_creator, 'create_clip', new_callable=unittest.mock.AsyncMock)
def test_api_create_clip_success(mock_create_clip_method): # Renamed and mock injected
    # Configure the mock
    # The Highlights field will default as per its model if not explicitly provided,
    # or if provided as Highlights(arr=[]) for empty highlights.
    # ClipResponse itself requires the 'highlights' argument.
    mock_create_clip_method.return_value = ClipResponse(
        clip_path="clips/test_clip.mp4",
        message="Clip created successfully",
        highlights=Highlights(arr=[]) # Explicitly providing default empty Highlights
    )

    # client = TestClient(app) # client is already defined globally
    response = client.post("/create_clip", json={ # Corrected endpoint
        "youtube_url": "http://some.fake.url/video.mp4",
        "start_time": 10,
        "duration": 5,
        "clip_name": "test_clip"
    })

    assert response.status_code == 200
    assert response.json() == {
        "clip_path": "clips/test_clip.mp4",
        "message": "Clip created successfully",
        "highlights": {"highlights": []} # Default empty highlights based on model structure
    }
    # Assert that the mocked method was called correctly
    mock_create_clip_method.assert_called_once()
    # Optionally, assert call arguments.
    # called_with_clip_request = mock_create_clip_method.call_args[0][0]
    # assert called_with_clip_request.youtube_url == "http://some.fake.url/video.mp4"


# New async unit test for ClipCreator.create_clip method
@unittest.mock.patch('backend.clip_creator.subprocess.run')
@unittest.mock.patch('backend.clip_creator.YouTube')
async def test_clip_creator_create_clip_success_with_name(mock_youtube, mock_subprocess_run):
    # Configure Mocks
    mock_yt_instance = mock_youtube.return_value
    mock_stream = mock_yt_instance.streams.get_highest_resolution.return_value
    # Use settings.DOWNLOAD_DIR for constructing the dummy download path
    downloaded_video_path = os.path.join(settings.DOWNLOAD_DIR, 'video.mp4') 
    mock_stream.download.return_value = downloaded_video_path
    mock_subprocess_run.return_value = unittest.mock.CompletedProcess(args=[], returncode=0)

    creator = ClipCreator() # Uses centralized settings now
    
    clip_name_to_test = "my_test_clip"
    request_data = ClipRequest(
        youtube_url="http://fake.youtube.url/watch?v=123",
        start_time=10,
        duration=5,
        clip_name=clip_name_to_test
    )

    response = await creator.create_clip(request_data)

    assert isinstance(response, ClipResponse)
    # Use settings.OUTPUT_DIR for the expected output path
    expected_output_path = os.path.join(settings.OUTPUT_DIR, f"{clip_name_to_test}.mp4")
    assert response.clip_path == expected_output_path
    
    # As per prompt: ClipResponse.message is Optional[str]=None
    # and create_clip returns ClipResponse(clip_path=output_path)
    # thus message should be None.
    assert response.message is None 
    
    # As per prompt: ClipResponse.highlights is Optional[Highlights] = Field(default_factory=...)
    # This means response.highlights will be a Highlights object with an empty list.
    assert response.highlights is not None 
    assert isinstance(response.highlights, Highlights)
    assert response.highlights.highlights == [] 

    # Assert mock calls
    mock_youtube.assert_called_once_with(request_data.youtube_url)
    mock_yt_instance.streams.get_highest_resolution.assert_called_once()
    # Assert download was called with settings.DOWNLOAD_DIR
    mock_stream.download.assert_called_once_with(output_path=settings.DOWNLOAD_DIR)
    
    expected_ffmpeg_cmd = [
        settings.FFMPEG_PATH, # Use centralized FFMPEG_PATH
        "-i", downloaded_video_path,
        "-ss", str(request_data.start_time),
        "-t", str(request_data.duration),
        "-c:v", "copy",
        "-c:a", "copy",
        expected_output_path,
    ]
    # Assert subprocess.run was called with check=True
    mock_subprocess_run.assert_called_once_with(expected_ffmpeg_cmd, check=True)


@unittest.mock.patch('backend.clip_creator.subprocess.run')
@unittest.mock.patch('backend.clip_creator.YouTube')
async def test_clip_creator_create_clip_success_default_name(mock_youtube, mock_subprocess_run):
    # Configure Mocks
    mock_yt_instance = mock_youtube.return_value
    mock_stream = mock_yt_instance.streams.get_highest_resolution.return_value
    # Use a distinct video name for clarity, though 'video.mp4' would also work if mocks are reset.
    downloaded_video_path = os.path.join(settings.DOWNLOAD_DIR, 'video_default.mp4') 
    mock_stream.download.return_value = downloaded_video_path
    mock_subprocess_run.return_value = unittest.mock.CompletedProcess(args=[], returncode=0)

    creator = ClipCreator() # Uses centralized settings
    
    request_data = ClipRequest(
        youtube_url="http://fake.youtube.url/watch?v=456", # Different URL for this test
        start_time=15,
        duration=10
        # clip_name is omitted, so it should use the default "clip"
    )

    response = await creator.create_clip(request_data)

    assert isinstance(response, ClipResponse)
    # Default clip name is "clip"
    expected_output_path = os.path.join(settings.OUTPUT_DIR, "clip.mp4")
    assert response.clip_path == expected_output_path
    
    # As per prompt/previous logic: ClipResponse.message is None
    assert response.message is None 
    
    # As per prompt/previous logic: ClipResponse.highlights is a default Highlights object
    assert response.highlights is not None 
    assert isinstance(response.highlights, Highlights)
    assert response.highlights.highlights == [] 

    # Assert mock calls
    mock_youtube.assert_called_once_with(request_data.youtube_url)
    mock_yt_instance.streams.get_highest_resolution.assert_called_once()
    mock_stream.download.assert_called_once_with(output_path=settings.DOWNLOAD_DIR)
    
    expected_ffmpeg_cmd = [
        settings.FFMPEG_PATH,
        "-i", downloaded_video_path,
        "-ss", str(request_data.start_time),
        "-t", str(request_data.duration),
        "-c:v", "copy",
        "-c:a", "copy",
        expected_output_path, # This uses "clip.mp4"
    ]
    mock_subprocess_run.assert_called_once_with(expected_ffmpeg_cmd, check=True)


# --- API Endpoint Error Tests for /create_clip ---

def test_api_create_clip_invalid_data_missing_field_422():
    # client = TestClient(app) # client is already defined globally
    response = client.post("/create_clip", json={
        # "youtube_url": "http://some.fake.url/video.mp4", # Missing youtube_url
        "start_time": 10,
        "duration": 5,
        "clip_name": "test_clip_422"
    })
    assert response.status_code == 422
    # Optional: More detailed check for Pydantic error structure
    # data = response.json()
    # assert data["detail"][0]["type"] == "missing" 
    # assert data["detail"][0]["loc"] == ['body', 'youtube_url']


@unittest.mock.patch.object(main_app_clip_creator, 'create_clip', new_callable=unittest.mock.AsyncMock)
def test_api_create_clip_value_error_from_service_400(mock_create_clip_method):
    mock_create_clip_method.side_effect = ValueError("Test value error from service")

    # client = TestClient(app) # client is already defined globally
    response = client.post("/create_clip", json={
        "youtube_url": "http://some.fake.url/video_for_400.mp4",
        "start_time": 10,
        "duration": 5,
        "clip_name": "test_clip_400"
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Test value error from service"}


@unittest.mock.patch.object(main_app_clip_creator, 'create_clip', new_callable=unittest.mock.AsyncMock)
def test_api_create_clip_generic_exception_from_service_500(mock_create_clip_method):
    exception_message = "Test generic exception from service"
    mock_create_clip_method.side_effect = Exception(exception_message)

    # client = TestClient(app) # client is already defined globally
    response = client.post("/create_clip", json={
        "youtube_url": "http://some.fake.url/video_for_500.mp4",
        "start_time": 10,
        "duration": 5,
        "clip_name": "test_clip_500"
    })
    assert response.status_code == 500
    # This assertion matches the error handling in main.py:
    # return JSONResponse(content={"error": "An unexpected error occurred", "detail": str(e)}, status_code=500)
    assert response.json() == {"error": "An unexpected error occurred", "detail": exception_message}