from fastapi import FastAPI
from fastapi.testclient import TestClient


from backend.models.clip_request import ClipRequest
from backend.clip_creator import ClipCreator
from backend.main import app

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
    response = client.post("/create_clip1", json=data)
    # assert response.status_code == 200
    # assert response.json()["message"] == "Clip created successfully"
    # Add more assertions as needed