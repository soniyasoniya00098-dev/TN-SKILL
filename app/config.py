import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# LOAD .ENV
# ============================================================

load_dotenv(BASE_DIR / ".env")


# ============================================================
# APPLICATION
# ============================================================

APP_NAME = os.getenv(
    "APP_NAME",
    "ComicCraft - AI Comic Story Creator",
).strip()


# ============================================================
# GEMINI API
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    "",
).strip()

GEMINI_OUTLINE_MODEL = os.getenv(
    "GEMINI_OUTLINE_MODEL",
    "gemini-3.8-flash",
).strip()

GEMINI_STORY_MODEL = os.getenv(
    "GEMINI_STORY_MODEL",
    "gemini-3.8-flash",
).strip()

GEMINI_IMAGE_MODEL = os.getenv(
    "GEMINI_IMAGE_MODEL",
    "gemini-3.1-flash-image",
).strip()


# ============================================================
# HUGGING FACE
# ============================================================

HF_TOKEN = os.getenv(
    "HF_TOKEN",
    "",
).strip()


# ============================================================
# IMAGE GENERATION
# ============================================================

IMAGE_PROVIDER = os.getenv(
    "IMAGE_PROVIDER",
    "gemini",
).strip().lower()

IMAGE_MODEL = os.getenv(
    "IMAGE_MODEL",
    "stabilityai/stable-diffusion-xl-base-1.0",
).strip()

LOCAL_IMAGE_MODEL = os.getenv(
    "LOCAL_IMAGE_MODEL",
    "runwayml/stable-diffusion-v1-5",
).strip()


# ============================================================
# IMAGE SIZE
# ============================================================

IMAGE_WIDTH = int(
    os.getenv(
        "IMAGE_WIDTH",
        "768",
    )
)

IMAGE_HEIGHT = int(
    os.getenv(
        "IMAGE_HEIGHT",
        "512",
    )
)


# ============================================================
# COMIC SETTINGS
# ============================================================

PANELS_COUNT = int(
    os.getenv(
        "PANELS_COUNT",
        "5",
    )
)


# ============================================================
# AI SETTINGS
# ============================================================

MOCK_AI = (
    os.getenv(
        "MOCK_AI",
        "false",
    ).strip().lower()
    == "true"
)

ALLOW_IMAGE_FALLBACK = (
    os.getenv(
        "ALLOW_IMAGE_FALLBACK",
        "false",
    ).strip().lower()
    == "true"
)


# ============================================================
# TIMEOUT
# ============================================================

REQUEST_TIMEOUT = int(
    os.getenv(
        "REQUEST_TIMEOUT",
        "180",
    )
)


# ============================================================
# DIRECTORIES
# ============================================================

STATIC_DIR = BASE_DIR / "static"

PANELS_DIR = STATIC_DIR / "panels"

EXPORTS_DIR = STATIC_DIR / "exports"

TEMPLATES_DIR = BASE_DIR / "templates"


# ============================================================
# CREATE DIRECTORIES
# ============================================================

STATIC_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

PANELS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

EXPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

TEMPLATES_DIR.mkdir(
    parents=True,
    exist_ok=True,
)