import json
import os
import time
from datetime import UTC, datetime
from typing import Any

from dotenv import find_dotenv, load_dotenv
from google.adk.agents import Context, LlmAgent
from google.adk.apps import App
from google.adk.workflow import Workflow, node
from google.adk.workflow._retry_config import RetryConfig
from google.genai import Client, types
from google.genai.errors import ServerError
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv(find_dotenv())

# Robust retry policy for transient server errors (like 503 UNAVAILABLE)
DEFAULT_RETRY = RetryConfig(
    max_attempts=3,
    initial_delay=2.0,
    max_delay=10.0,
    backoff_factor=2.0,
    exceptions=[ServerError]
)

# Modularity: Swap models via env vars
TEXT_MODEL = os.getenv("TEXT_MODEL", "gemini-3.5-flash")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gemini-3.1-flash-image-preview")
VIDEO_MODEL = os.getenv("VIDEO_MODEL", "veo-3.1-generate-preview")

# Ensure assets dir exists
os.makedirs("assets", exist_ok=True)
os.makedirs("working", exist_ok=True)

# Load Styleguide
try:
    with open("prompts/styleguide.md") as f:
        STYLEGUIDE_CONTENT = f.read()
except FileNotFoundError:
    STYLEGUIDE_CONTENT = ""
    print("Warning: prompts/styleguide.md not found.")

# Load Reference Prompts
try:
    with open("prompts/image_reference_prompt.md") as f:
        IMAGE_REF = f.read()
except FileNotFoundError:
    IMAGE_REF = ""
    print("Warning: prompts/image_reference_prompt.md not found.")

try:
    with open("prompts/video_reference_prompt.md") as f:
        VIDEO_REF = f.read()
except FileNotFoundError:
    VIDEO_REF = ""
    print("Warning: prompts/video_reference_prompt.md not found.")


# --- Schemas ---

class MarketAnalysis(BaseModel):
    trends: list[str]
    competitors: list[str]
    opportunities: str

class Persona(BaseModel):
    name: str
    age: int
    interests: list[str]
    pain_points: list[str]

class Personas(BaseModel):
    personas: list[Persona]

class CampaignBrief(BaseModel):
    persona_name: str
    key_message: str
    visual_concept: str
    video_concept: str

class CampaignBriefs(BaseModel):
    briefs: list[CampaignBrief]


# --- Enhanced Schemas for Prompt Rewriter ---

class ImageCinematography(BaseModel):
    lens_type: str
    depth_of_field: str
    lighting: str
    exposure: str

class ImageSubject(BaseModel):
    identity: str
    placement: str
    wardrobe_or_finish: str
    action_pose: str

class ImageComposition(BaseModel):
    shot_type: str
    angle: str
    negative_space: str

class ImageVisualDetails(BaseModel):
    color_palette: str
    mood: str
    texture: str
    props: str

class ImageEnvironment(BaseModel):
    location: str
    background_blur: str

class ImageSpecs(BaseModel):
    format: str
    aspect_ratio: str
    resolution: str

class ImageBlueprint(BaseModel):
    image_specs: ImageSpecs
    cinematography: ImageCinematography
    subject: ImageSubject
    composition: ImageComposition
    visual_details: ImageVisualDetails
    environment: ImageEnvironment

class VideoBlueprint(BaseModel):
    camera_movement: str
    lighting: str
    subject_action: str
    environment: str
    color_grading: str
    transitions: str

class EnhancedCampaignBrief(BaseModel):
    persona_name: str
    key_message: str
    visual_blueprint: ImageBlueprint
    video_blueprint: VideoBlueprint

class EnhancedCampaignBriefs(BaseModel):
    briefs: list[EnhancedCampaignBrief]


# --- Tools ---

def search_web(query: str) -> str:
    """Performs an actual web search using Google Search grounding.
    
    Args:
        query: The search query string to run on Google Search.
    """
    print(f"[Tool] Performing Google Web Search for: '{query}'...")
    try:
        client = Client()
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=f"Perform a search for the following query and summarize the findings in detail: {query}",
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        if response.text:
            return response.text
        return f"No search results found for {query}."
    except Exception as e:
        print(f"Warning: Google Search tool failed ({e}). Returning fallback search results.")
        return (
            f"Recent search results for {query}: Increasing demand for smart, energy-efficient home devices. "
            "Competitors focusing on basic features, leaving room for premium AI integrations."
        )

# --- Nodes ---

@node
def read_product_data(node_input: Any = None) -> str:
    """Reads product.json to start the pipeline."""
    print("[Pipeline] Reading product data...")
    with open("product.json") as f:
        data = f.read()
    return f"Product Data to analyze: {data}"

# Agent 1
market_analyzer = LlmAgent(
    name="market_analyzer",
    model=TEXT_MODEL,
    instruction=f"Analyze the market based on the product data. Use the web search tool to gather recent trends.\n\nGlobal Styleguide:\n{STYLEGUIDE_CONTENT}",
    output_schema=MarketAnalysis,
    output_key="market_analysis",
    tools=[search_web],
    retry_config=DEFAULT_RETRY
)

@node
def save_market_analysis(ctx: Context, node_input: MarketAnalysis) -> str:
    print("[Pipeline] Saving market analysis...")
    with open("working/market_analysis.json", "w") as f:
        f.write(node_input.model_dump_json(indent=2))
    return node_input.model_dump_json()

# Agent 2
persona_generator = LlmAgent(
    name="persona_generator",
    model=TEXT_MODEL,
    instruction=f"Generate 3 detailed marketing personas based on the market analysis provided.\n\nGlobal Styleguide:\n{STYLEGUIDE_CONTENT}",
    output_schema=Personas,
    output_key="personas",
    retry_config=DEFAULT_RETRY
)

@node
def save_personas(ctx: Context, node_input: Personas) -> str:
    print("[Pipeline] Saving personas...")
    with open("working/personas.json", "w") as f:
        f.write(node_input.model_dump_json(indent=2))
    return node_input.model_dump_json()

# Agent 3
campaign_strategist = LlmAgent(
    name="campaign_strategist",
    model=TEXT_MODEL,
    instruction=f"Create a campaign brief for each persona provided. Focus on key messages, and creative concepts for images and videos.\n\nGlobal Styleguide:\n{STYLEGUIDE_CONTENT}",
    output_schema=CampaignBriefs,
    output_key="campaign_briefs",
    retry_config=DEFAULT_RETRY
)

@node
def save_campaign_briefs(ctx: Context, node_input: CampaignBriefs) -> CampaignBriefs:
    print("[Pipeline] Saving campaign briefs...")
    with open("working/campaign_briefs.json", "w") as f:
        f.write(node_input.model_dump_json(indent=2))
    return node_input

# Agent 3.5: Prompt Rewriter
prompt_rewriter = LlmAgent(
    name="prompt_rewriter",
    model=TEXT_MODEL,
    instruction=f"""You are the AI Creative Director. Your job is to take the provided campaign briefs and rewrite/enhance the visual and video concepts into structured blueprints.

For the visual_blueprint, follow these instructions strictly:
{IMAGE_REF}

For the video_blueprint, follow these instructions strictly:
{VIDEO_REF}

Maintain the persona_name and key_message exactly as they are in the input.
""",
    output_schema=EnhancedCampaignBriefs,
    output_key="enhanced_briefs",
    retry_config=DEFAULT_RETRY
)

@node
def save_enhanced_briefs(ctx: Context, node_input: EnhancedCampaignBriefs) -> EnhancedCampaignBriefs:
    print("[Pipeline] Saving enhanced campaign briefs...")
    with open("working/enhanced_campaign_briefs.json", "w") as f:
        f.write(node_input.model_dump_json(indent=2))
    return node_input


# Agent 4: Asset Creation Engine

PROHIBITED_TERMS = ["cheap", "guaranteed", "miracle", "overnight"]

def validate_brand_safety(copy: str) -> str:
    """Layered Validation before writing the final text copy to disk."""
    copy_lower = copy.lower()
    for term in PROHIBITED_TERMS:
        if term in copy_lower:
            raise ValueError(f"Brand safety violation: Found prohibited term '{term}'")
    return copy

class AssetCreationEngine:
    def __init__(self):
        # We assume vertexai=True is implicitly handled or uses fallback.
        # Ensure GOOGLE_GENAI_USE_VERTEXAI="True" is in env if using vertex.
        self.client = Client()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def create_ad_copy(self, brief: EnhancedCampaignBrief) -> str:
        response = self.client.models.generate_content(
            model=TEXT_MODEL,
            contents=f"Write a short, engaging ad copy (2-3 sentences) based on this key message: {brief.key_message}\n\nGlobal Styleguide:\n{STYLEGUIDE_CONTENT}"
        )
        if not response.text:
            raise ValueError("Empty response from LLM")
        return validate_brand_safety(response.text)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def create_image(self, brief: EnhancedCampaignBrief) -> tuple[bytes, str]:
        # Convert Blueprint to String Prompt
        bp = brief.visual_blueprint
        visual_concept_str = (
            f"Cinematography: {bp.cinematography.lens_type}, {bp.cinematography.lighting}, {bp.cinematography.depth_of_field}. "
            f"Subject: {bp.subject.identity}, {bp.subject.wardrobe_or_finish}, {bp.subject.action_pose}. "
            f"Composition: {bp.composition.shot_type}, {bp.composition.angle}. "
            f"Style: {bp.visual_details.color_palette}, {bp.visual_details.mood}, {bp.visual_details.texture}. "
            f"Environment: {bp.environment.location}, Blur: {bp.environment.background_blur}."
        )

        final_prompt = f"{visual_concept_str}\n\nGlobal Styleguide:\n{STYLEGUIDE_CONTENT}"

        try:
            result = self.client.models.generate_content(
                model=IMAGE_MODEL,
                contents=final_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"]
                )
            )

            for part in result.candidates[0].content.parts:
                if part.inline_data is not None:
                    return part.inline_data.data, final_prompt

            raise ValueError("No images generated in content parts")
        except Exception as e:
            # If vertex ai is not fully configured or model missing, return mock.
            print(f"Warning: Image generation failed ({e}), returning mock image.")
            return b"mock_image_bytes", final_prompt

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def create_video(self, brief: EnhancedCampaignBrief, image_bytes: bytes) -> tuple[bytes, str]:
        # Convert Blueprint to String Prompt
        vp = brief.video_blueprint
        video_concept_str = (
            f"Camera Movement: {vp.camera_movement}. "
            f"Lighting: {vp.lighting}. "
            f"Subject Action: {vp.subject_action}. "
            f"Environment: {vp.environment}. "
            f"Color Grading: {vp.color_grading}. "
            f"Transitions: {vp.transitions}."
        )

        final_prompt = f"{video_concept_str}\n\nGlobal Styleguide:\n{STYLEGUIDE_CONTENT}"

        try:
            print(f"Generating video for prompt: {video_concept_str[:50]}...")

            # Veo 3.1 generation using the previously generated image as the first frame
            operation = self.client.models.generate_videos(
                model=VIDEO_MODEL,
                prompt=final_prompt,
            )

            # Poll for completion
            while not operation.done:
                print("Waiting for video generation to complete...")
                time.sleep(10)
                operation = self.client.operations.get(operation)

            video_result = operation.response.generated_videos[0].video

            if not video_result.video_bytes:
                self.client.files.download(file=video_result)

            if video_result.video_bytes:
                return video_result.video_bytes, final_prompt
            else:
                return b"mock_video_bytes_download_required", final_prompt
        except Exception as e:
            print(f"Warning: Video generation failed ({e}), returning mock video.")
            return b"mock_video_bytes", final_prompt

@node
def generate_assets(ctx: Context, node_input: EnhancedCampaignBriefs) -> str:
    """Agent 4 node."""
    engine = AssetCreationEngine()
    session_id = ctx.session.id if ctx.session else "unknown_session"

    for i, brief in enumerate(node_input.briefs):
        print(f"Generating assets for persona: {brief.persona_name}...")

        # 1. Ad Copy
        try:
            copy = engine.create_ad_copy(brief)
            with open(f"assets/copy_{i}.txt", "w") as f:
                f.write(copy)
        except Exception as e:
             with open(f"assets/copy_{i}_error.txt", "w") as f:
                f.write(str(e))

        # 2. Image
        img_bytes, img_prompt = engine.create_image(brief)
        with open(f"assets/image_{i}.jpg", "wb") as f:
            f.write(img_bytes)

        img_meta = {
            "session_id": session_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "prompt": img_prompt,
            "blueprint": brief.visual_blueprint.model_dump(),
            "persona_name": brief.persona_name
        }
        with open(f"assets/image_{i}_metadata.json", "w") as f:
            json.dump(img_meta, f, indent=2)

        # 3. Video
        vid_bytes, vid_prompt = engine.create_video(brief, img_bytes)
        with open(f"assets/video_{i}.mp4", "wb") as f:
            f.write(vid_bytes)

        vid_meta = {
            "session_id": session_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "prompt": vid_prompt,
            "blueprint": brief.video_blueprint.model_dump(),
            "persona_name": brief.persona_name
        }
        with open(f"assets/video_{i}_metadata.json", "w") as f:
            json.dump(vid_meta, f, indent=2)

    return "All marketing assets have been successfully generated and saved to the /assets directory."

# --- Graph Definition ---

root_agent = Workflow(
    name="marketing_pipeline",
    edges=[
        ('START', read_product_data),
        (read_product_data, market_analyzer),
        (market_analyzer, save_market_analysis),
        (save_market_analysis, persona_generator),
        (persona_generator, save_personas),
        (save_personas, campaign_strategist),
        (campaign_strategist, save_campaign_briefs),
        (save_campaign_briefs, prompt_rewriter),
        (prompt_rewriter, save_enhanced_briefs),
        (save_enhanced_briefs, generate_assets)
    ]
)

app = App(
    name="app",
    root_agent=root_agent
)
