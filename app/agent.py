# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.firestore_tools import get_training_routines, save_training_routine


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


def calculate_heart_rate_zones(resting_hr: int, max_hr: int) -> dict:
    """Calculates Karvonen heart rate training zones (Zone 1 through Zone 5) based on resting and max heart rate.

    Args:
        resting_hr: The runner's resting heart rate in beats per minute (bpm).
        max_hr: The runner's maximum heart rate in beats per minute (bpm).

    Returns:
        A dictionary containing bpm target ranges for training Zones 1 to 5.
    """
    hrr = max_hr - resting_hr
    return {
        "Zone 1 (Recovery)": f"{round(resting_hr + hrr * 0.50)} - {round(resting_hr + hrr * 0.60)} bpm",
        "Zone 2 (Aerobic/Easy)": f"{round(resting_hr + hrr * 0.60)} - {round(resting_hr + hrr * 0.70)} bpm",
        "Zone 3 (Tempo)": f"{round(resting_hr + hrr * 0.70)} - {round(resting_hr + hrr * 0.80)} bpm",
        "Zone 4 (Threshold)": f"{round(resting_hr + hrr * 0.80)} - {round(resting_hr + hrr * 0.90)} bpm",
        "Zone 5 (Anaerobic/Max)": f"{round(resting_hr + hrr * 0.90)} - {round(max_hr)} bpm",
    }


def get_running_weather_forecast(latitude: float, longitude: float) -> dict:
    """Fetches real-time outdoor running weather conditions (temperature, humidity, wind speed) from the free Open-Meteo public API.

    Args:
        latitude: Latitude coordinate of the running location (e.g., 40.7128 for NYC, 37.7749 for SF).
        longitude: Longitude coordinate of the running location (e.g., -74.0060 for NYC, -122.4194 for SF).

    Returns:
        A dictionary with real-time temperature, apparent feels-like temperature, humidity, and wind speed.
    """
    import json
    import urllib.request

    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PaceCraftAI/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            current = data.get("current", {})
            return {
                "latitude": latitude,
                "longitude": longitude,
                "temperature_celsius": current.get("temperature_2m"),
                "feels_like_celsius": current.get("apparent_temperature"),
                "humidity_percent": current.get("relative_humidity_2m"),
                "wind_speed_kmh": current.get("wind_speed_10m"),
                "summary": (
                    f"Temp: {current.get('temperature_2m')}°C (Feels like {current.get('apparent_temperature')}°C), "
                    f"Humidity: {current.get('relative_humidity_2m')}%, Wind: {current.get('wind_speed_10m')} km/h"
                ),
            }
    except Exception as e:
        return {"error": f"Failed to fetch running weather forecast: {str(e)}"}


def consult_herbal_docs(query: str) -> str:
    """Search the herbal corpus (Nicholas Culpeper's The Complete Herbal) and return matched passages for herbal remedies, plants, and natural health.

    Args:
        query: Plant, herb, remedy, or health topic to look up.

    Returns:
        Matched passages from the herbal corpus.
    """
    import os
    import vertexai
    from vertexai.preview import rag

    corpus_name = "projects/417513954591/locations/us-central1/ragCorpora/herbal-corpus"
    try:
        vertexai.init(project="qwiklabs-gcp-03-3e15bc834bf2", location="us-central1")
        resp = rag.retrieval_query(
            text=query,
            rag_resources=[rag.RagResource(rag_corpus=corpus_name)],
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=5),
        )
        contexts = getattr(resp.contexts, "contexts", [])
        passages = [c.text.strip() for c in contexts if getattr(c, "text", "").strip()]
        if passages:
            return "\n\n---\n\n".join(passages)
    except Exception:
        pass

    file_path = os.path.join(os.path.dirname(__file__), "..", "data", "pg49513.txt")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 50]
        query_words = set(query.lower().split())
        matched = []
        for p in paragraphs:
            score = sum(1 for w in query_words if w in p.lower())
            if score > 0:
                matched.append((score, p[:500]))
        matched.sort(key=lambda x: x[0], reverse=True)
        results = [m[1] for m in matched[:5]]
        if results:
            return "\n\n---\n\n".join(results)
    return "No relevant herbal passage found."


def generate_running_gear_image(item_description: str) -> str:
    """Generates an image for running shoes, endurance gear, marathon apparel, or athletic items using gemini-3.1-flash-lite-image in the global region.
    Saves the image locally as an artifact, uploads it to Cloud Storage, and returns the public URL.

    Args:
        item_description: Description of the running gear or endurance item to generate an image for.

    Returns:
        The public Cloud Storage URL of the generated image.
    """
    import os
    import uuid
    from google import genai
    from google.cloud import storage

    project_id = "qwiklabs-gcp-03-3e15bc834bf2"
    bucket_name = "pacecraft-ai-assets-qwiklabs-gcp-03-3e15bc834bf2"

    try:
        client = genai.Client(project=project_id, location="global", vertexai=True)
        prompt = f"Professional studio product photograph of {item_description} for runners, high quality"
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
        )

        image_bytes = None
        mime_type = "image/jpeg"
        for part in response.candidates[0].content.parts:
            if getattr(part, "inline_data", None):
                image_bytes = part.inline_data.data
                mime_type = getattr(part.inline_data, "mime_type", None) or mime_type
                break

        if not image_bytes:
            return "Error: No image content generated."

        ext = ".png" if "png" in mime_type else ".jpg"
        filename = f"gear_{uuid.uuid4().hex[:8]}{ext}"

        artifact_dir = os.path.join(os.path.dirname(__file__), "..", "data", "generated_images")
        os.makedirs(artifact_dir, exist_ok=True)
        local_path = os.path.join(artifact_dir, filename)
        with open(local_path, "wb") as f:
            f.write(image_bytes)

        storage_client = storage.Client(project=project_id)
        bucket = storage_client.bucket(bucket_name)
        blob_path = f"generated_images/{filename}"
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(local_path, content_type=mime_type)

        try:
            blob.make_public()
        except Exception:
            pass

        public_url = f"https://storage.googleapis.com/{bucket_name}/{blob_path}"
        return f"Generated gear image successfully: {public_url}"
    except Exception as e:
        return f"Failed to generate image: {str(e)}"


async def generate_running_video(prompt: str, tool_context: ToolContext) -> str:
    """Generates a short video for running, marathon events, athletic gear, or endurance coaching using gemini-omni-flash-preview in the global region.
    Saves the video as an artifact in the Playground session and uploads it directly to Cloud Storage, returning the public HTTPS URL.

    Args:
        prompt: Description of the running video clip to generate.
        tool_context: ToolContext for saving the video artifact to the agent session.

    Returns:
        The public Cloud Storage URL of the generated video.
    """
    import base64
    import uuid
    from google import genai
    from google.genai import types
    from google.cloud import storage

    project_id = "qwiklabs-gcp-03-3e15bc834bf2"
    bucket_name = "pacecraft-ai-assets-qwiklabs-gcp-03-3e15bc834bf2"

    try:
        client = genai.Client(project=project_id, location="global", vertexai=True)
        response = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=f"A short video for runners: {prompt}",
        )

        output_video = getattr(response, "output_video", None)
        if not output_video or not getattr(output_video, "data", None):
            return "Error: No video content returned from Gemini Omni model."

        raw_data = output_video.data
        if isinstance(raw_data, str):
            video_bytes = base64.b64decode(raw_data)
        else:
            video_bytes = raw_data

        mime_type = getattr(output_video, "mime_type", None) or "video/mp4"
        ext = ".webm" if "webm" in mime_type else ".mp4"
        filename = f"video_{uuid.uuid4().hex[:8]}{ext}"

        # 1. Save artifact to Playground session via tool_context
        if tool_context:
            artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
            await tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload video bytes to public Cloud Storage bucket without writing to local file
        storage_client = storage.Client(project=project_id)
        bucket = storage_client.bucket(bucket_name)
        blob_path = f"generated_videos/{filename}"
        blob = bucket.blob(blob_path)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        try:
            blob.make_public()
        except Exception:
            pass

        public_url = f"https://storage.googleapis.com/{bucket_name}/{blob_path}"
        return f"Generated video successfully: {public_url}"
    except Exception as e:
        return f"Failed to generate video: {str(e)}"


async def generate_memories_callback(callback_context: CallbackContext):
    """Sends session turns to Vertex AI Memory Bank for durable fact extraction."""
    try:
        await callback_context.add_session_to_memory()
    except ValueError:
        pass
    return None


from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from .a2ui_utils import a2ui_callback

REASONING_ENGINE_RESOURCE = "projects/417513954591/locations/us-central1/reasoningEngines/8546622080202833920"

sandbox_code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=REASONING_ENGINE_RESOURCE
)

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are PaceCraft AI, a helpful running and endurance coach. "
        "You remember the user's stated fitness goals, target race distances, target finish times, "
        "and personal preferences from previous conversations to personalize your responses. "
        "CRITICAL: You MUST pay strict attention to and remember all user allergies (food, environmental, medication, dietary restrictions). "
        "Always review preloaded memories for any listed allergies before making nutritional, hydration, or training recommendations. "
        "Use calculate_heart_rate_zones to calculate precise training zones for runners when given their heart rate stats. "
        "Use get_running_weather_forecast to fetch live outdoor running weather conditions given lat/lng coordinates. "
        "Use consult_herbal_docs to look up natural herbs, plant remedies, and botanical information from Culpeper's Herbal. "
        "Use generate_running_gear_image to create realistic image previews of running shoes, apparel, marathon gear, or athletic equipment using gemini-3.1-flash-lite-image in global region and return public image URLs. "
        "Use generate_running_video to create short videos for running routines, marathon events, athletic gear, or form visualizations using gemini-omni-flash-preview in global region. "
        "Use the training_routines tools (get_training_routines, save_training_routine) to search for or save running routines stored in Firestore. "
        "You can execute Python code in a secure sandbox when calculations, data transformations, or simulations are requested."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=sandbox_code_executor,
    instruction=a2ui_instruction,
    tools=[
        get_weather,
        get_current_time,
        calculate_heart_rate_zones,
        get_running_weather_forecast,
        consult_herbal_docs,
        generate_running_gear_image,
        generate_running_video,
        get_training_routines,
        save_training_routine,
        PreloadMemoryTool(),
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)

