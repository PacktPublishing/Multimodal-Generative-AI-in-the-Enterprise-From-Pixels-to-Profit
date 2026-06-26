# Copyright 2026
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

import os
from pathlib import Path

import google.auth
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging

from app.app_utils.telemetry import setup_telemetry
from app.app_utils.typing import Feedback

setup_telemetry()
_, project_id = google.auth.default()
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

# Artifact bucket for ADK (created by Terraform, passed via env var)
logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# In-memory session configuration - no persistent storage
session_service_uri = None

artifact_service_uri = f"gs://{logs_bucket_name}" if logs_bucket_name else None

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=artifact_service_uri,
    allow_origins=allow_origins,
    session_service_uri=session_service_uri,
    otel_to_cloud=True,
)
app.title = "marketing-pipeline"
app.description = "API for interacting with the Agent marketing-pipeline"

# Mount static files
app.mount("/assets", StaticFiles(directory=os.path.join(AGENT_DIR, "assets")), name="assets")
app.mount("/working", StaticFiles(directory=os.path.join(AGENT_DIR, "working")), name="working")


@app.get("/api/latest-results")
def get_latest_results() -> dict[str, list[str]]:
    """List all generated files in assets and working directories."""
    assets_dir = Path(os.path.join(AGENT_DIR, "assets"))
    working_dir = Path(os.path.join(AGENT_DIR, "working"))

    results = {"assets": [], "working": []}

    if assets_dir.exists():
        results["assets"] = [f.name for f in assets_dir.iterdir() if f.is_file()]
    if working_dir.exists():
        results["working"] = [f.name for f in working_dir.iterdir() if f.is_file()]

    return results


import json

from fastapi import HTTPException
from pydantic import BaseModel


class ProductData(BaseModel):
    product_name: str
    description: str
    target_audience: str
    features: list[str]

@app.get("/api/product-data")
def get_product_data() -> dict:
    """Read the product.json file."""
    product_file = Path(os.path.join(AGENT_DIR, "product.json"))
    if not product_file.exists():
        return {}
    try:
        with open(product_file) as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read product data: {e}")

@app.post("/api/product-data")
def update_product_data(data: ProductData) -> dict[str, str]:
    """Update the product.json file."""
    product_file = Path(os.path.join(AGENT_DIR, "product.json"))
    try:
        with open(product_file, "w") as f:
            json.dump(data.model_dump(), f, indent=2)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write product data: {e}")

@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """Collect and log feedback.

    Args:
        feedback: The feedback data to log

    Returns:
        Success message
    """
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
