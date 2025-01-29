from pytube import YouTube

import subprocess
import os
import json

from google import genai
from google.genai import types

from .models.clip_request import ClipRequest  
from .models.clip_response import ClipResponse, Highlights, Highlight

class ClipCreator:
    def __init__(self, download_dir="downloads", output_dir="clips", ffmpeg_path="ffmpeg"):
        self.download_dir = os.environ.get("DOWNLOAD_DIR", download_dir)
        self.output_dir = os.environ.get("OUTPUT_DIR", output_dir)
        self.ffmpeg_path = os.environ.get("FFMPEG_PATH", ffmpeg_path)
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    async def create_clip(self, data: ClipRequest) -> ClipResponse: 
        youtube_url = data.youtube_url
        start_time = data.start_time
        duration = data.duration
        clip_name = data.clip_name or "clip"

        if not youtube_url or not start_time or not duration:
            raise ValueError("Missing required parameters")

        download_path = ""
        try:
            yt = YouTube(youtube_url)
            stream = yt.streams.get_highest_resolution()
            download_path = stream.download(output_path=self.download_dir)

        except Exception as e:
            print(e)
            raise e
        
        try:
            output_path = os.path.join(self.output_dir, f"{clip_name}.mp4")

            ffmpeg_command = [
                self.ffmpeg_path,
                "-i", download_path,
                "-ss", str(start_time),
                "-t", str(duration),
                "-c:v", "copy",
                "-c:a", "copy",
                output_path,
            ]

            subprocess.run(ffmpeg_command, check=True)
            response = ClipResponse(clip_path=output_path) 
            return response
            
        except Exception as e:
            #TODO: Add logging
            raise HTTPException(status_code=404, detail=f"Error creating clip: {e}")
            

    async def generate_highlights(self, data: ClipRequest, model = "gemini-1.5-pro-002") -> ClipResponse: 

        youtube_url = data.youtube_url

        client = genai.Client(
            vertexai=True,
            project="ml-demo-384110",
            location="us-central1"
        )

        video1 = types.Part.from_uri(
            file_uri=youtube_url,
            mime_type="video/*",
        )


        prompt = """SYSTEM: ```You are a expert in content creation and generation. You never miss any key frames in the video which can be used for video thumbnail or marketing campaign creation from any videos```
    INSTRUCTIONS: ```Recommend a set of top 4 frame timestamps for a best youtube thumbnail that can be recommended for this video. Generate a response in a JSON format.```
    OUTPUT: ```
    JSON
    [
    {
    timestamp: \"\",
    reasoning: \"\"
    }
    ]```"""



        text1 = types.Part.from_text(prompt)
            #"""You are given a video about \"the most searched something\" on Google Search. Please watch the video and generate structured description of it. The description should include a short summary no more than 100 words, followed by descriptions for each most searched something mentioned in the video. Use a time-dependent JSON format for the description as follows: {\"Summary\": <summary of the video, less than 100 words>, \"Details\": [ {\"MM:SS~MM:SS\" : { \"the most searched first step in history\": \"Moon landing by Neil Armstrong\"}}, {\"MM:SS-MM:SS\": {\"the most searched sport\": \"soccer\"}, ... ] }.""")

        
        
        contents = [
        types.Content(
            role="user",
            parts=[
            video1,
            text1
            ]
        )
        ]
        generate_content_config = types.GenerateContentConfig(
        temperature = 1,
        top_p = 0.95,
        max_output_tokens = 8192,
        response_mime_type = "application/json",
        safety_settings = [types.SafetySetting(
            category="HARM_CATEGORY_HATE_SPEECH",
            threshold="OFF"
        ),types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="OFF"
        ),types.SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
            threshold="OFF"
        ),types.SafetySetting(
            category="HARM_CATEGORY_HARASSMENT",
            threshold="OFF"
        )],
        )

        response= client.models.generate_content(
            model = model,
            contents = contents,
            config = generate_content_config,
        )
        highlights_json = json.loads(response.text)
        highlights =Highlights(highlights_json)
        if len(highlights_json) > 0:
            message="Highlights generated"
        else:
            message="No highlights detected"
        
        response = ClipResponse(highlights=highlights, message=message)
        return response
                